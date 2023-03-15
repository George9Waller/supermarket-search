from peewee import fn

from database import Product, Category

print('There are', Product.select().count(), 'products in the database')

sugar_per_money = (((Product.weight_in_g / 100.0) * Product.sugar_per_100g) / Product.price).alias('sugar_per_money')
sugar_per_money = Product.select(Product, sugar_per_money).where(Product.weight_in_g.is_null(False), Product.is_available).order_by(sugar_per_money.desc()).limit(100)

for index, item in enumerate(sugar_per_money):
    print('\n', index + 1, ':', item.name, '|', f'£{item.price}', '|',f'{item.weight_in_g}g', '|', f'{item.sugar_per_100g}g sugar per 100g', '|', f'{item.sugar_per_money}g sugar per £', '|', item.detail_url)
