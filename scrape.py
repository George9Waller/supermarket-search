import base64
import json
import re
import requests
import time

from bs4 import BeautifulSoup as bs
from peewee import Value
from urllib import parse

from database import db, Product, Category, Ingredient

UPDATE_EXISTING = False

KCAL = 'energy'
FAT = 'fat'
SATURATES = 'saturates'
CARBS = 'carbohydrate'
SUGAR = 'sugar'
FIBRE = 'fibre'
PROTEIN = 'protein'
SALT = 'salt'


def clean_value(value):
    lower_no_space = value.lower().replace(' ', '').replace(',', '.')
    text = re.sub(r'\((.*?)\)', '', lower_no_space.strip().split('/')[0])
    text = re.sub('[^0-9.]', '', text)
    if not text:
        return '0'
    if '%' in text:
        return '0'
    if re.search(r'[0-9]*mg', lower_no_space):
        return str(float(text) / 1000)
    return text


def get_nutrition_data(details_html):
    if details_html:
        html = base64.b64decode(details_html)
        content = bs(html, 'html.parser')
        nutritional_table = content.find('table', {'class': 'nutritionTable'})
    else:
        nutritional_table = None

    def get_nutrition_value(key):
        if nutritional_table:
            rows = nutritional_table.find_all(lambda tag: tag.name == 'tr' and tag.find('th') and key in tag.find('th').text.lower())
            if len(rows) > 0:
                row = rows[0]
                if key != KCAL and len(rows) > 1:
                    row = rows[1]
                if row and row.find('td'):
                    per_100 = row.find('td').text.lower()
                    # special case calories
                    if key == KCAL:
                        # kj
                        kj_matches = re.search(r'(.+?)kj', per_100.replace(' ', ''))
                        if kj_matches:
                            return float(clean_value(kj_matches.group(1))) / 4.184
                        # kcal
                        kcal_matches = re.search(r'(.+?)kcal', per_100.replace(' ', ''))
                        if kcal_matches:
                            return float(clean_value(kcal_matches.group(1)))

                    else:
                        return float(clean_value(per_100))

        return 0.0

    return {
        KCAL: get_nutrition_value(KCAL),
        FAT: get_nutrition_value(FAT),
        SATURATES: get_nutrition_value(SATURATES),
        CARBS: get_nutrition_value(CARBS),
        SUGAR: get_nutrition_value(SUGAR),
        FIBRE: get_nutrition_value(FIBRE),
        PROTEIN: get_nutrition_value(PROTEIN),
        SALT: get_nutrition_value(SALT),
    }


def get_categories(data):
    for category in data['categories']:
        yield Category.get_or_create(sainsburys_id=category['id'], name=category['name'])


def check_response(response):
    if not str(response.status_code)[0] == '2':
        raise Exception(f'Failed to get data {response.url} status', response.status_code, bs(response.content, 'html.parser').text)
    return response


db.connect()
db.create_tables(
    [
        Product,
        Category,
        Ingredient,
        Product.categories.get_through_model(),
        Product.ingredients.get_through_model()
    ],
    safe=True
)
db.close()

failed = []

# sitemaps
sitemaps_data = check_response(requests.get('https://www.sainsburys.co.uk/sitemap.xml'))
sitemaps = bs(sitemaps_data.content, 'xml').find_all('loc')

for sitemap in sitemaps:
    # get individual sitemap content
    sitemap_data = check_response(requests.get(sitemap.text))
    items = bs(sitemap_data.content, 'xml').find_all('loc')

    # iterate over all the product pages
    groceries = list(filter(lambda a: '/product/' in a.text, items))
    sitemap_items_count = len(groceries)
    print(sitemap_items_count, ' items in sitemap ', sitemap.text)

    for index, item in enumerate(groceries):
        try:
            product_path = item.text.split('/')[-1]

            if Product.select().where(Value(Product.detail_url).endswith(parse.quote(product_path))).count() > 0:
                continue

            page = check_response(requests.get(f'https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?filter[product_seo_url]=gb/groceries/{product_path}'))

            data = json.loads(page.content).get('products')[0]
            print(index + 1, 'out of', sitemap_items_count, ':', data['product_uid'], data['full_url'])

            product_existing = Product.select().where(Product.sainsburys_id == data['product_uid']).count() > 0
            if product_existing and UPDATE_EXISTING:
                raise NotImplementedError('Updating existing products not implemented yet')

            if not product_existing:
                nutritional_data = get_nutrition_data(data.get('details_html'))
                price = 0.0
                if data.get('retail_price'):
                    price = data['retail_price']['price']
                elif data.get('catchweight'):
                    price = data['catchweight'][0]['retail_price']['price']

                product = Product.create(
                    sainsburys_id=data['product_uid'],
                    name=data['name'],
                    price=price,
                    average_rating=data['reviews']['average_rating'],
                    description='\n'.join(data['description']),
                    brand=' '.join(data['attributes'].get('brand', [])) if data.get('attributes') else '',
                    detail_url=data['full_url'],
                    is_available=data.get('is_available'),
                    kcal_per_100g=nutritional_data[KCAL],
                    fat_per_100g=nutritional_data[FAT],
                    saturates_per_100g=nutritional_data[SATURATES],
                    carbs_per_100g=nutritional_data[CARBS],
                    sugar_per_100g=nutritional_data[SUGAR],
                    fibre_per_100g=nutritional_data[FIBRE],
                    protein_per_100g=nutritional_data[PROTEIN],
                    salt_per_100g=nutritional_data[SALT],
                )
                categories = [category for category, _ in list(get_categories(data))]
                if categories:
                    product.categories.add(categories)
                product.save()

            time.sleep(1)

        except Exception as e:
            print('FAILED: ', e)
            failed.append(item.text)
            time.sleep(0.5)

if len(failed) > 0:
    for url in failed:
        print(url)

    print(len(failed), 'have failed')
