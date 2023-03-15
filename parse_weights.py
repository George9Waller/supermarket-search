import re

from database import Product


def get_multi_regex(unit):
    return f'\s[0-9]+\s*x\s*[0-9.]+{unit}', f'x\s*[0-9.]+{unit}'


def get_single_regex(unit):
    return f'\s[0-9.]+{unit}'


def set_weight(product, match, multiplier = 1):
    product.weight_in_g = float(re.sub('[^0-9.]', '', match.group(0))) * multiplier
    product.save()


for product in Product.select().where(Product.weight_in_g.is_null()):
    name = product.name.lower()

    r_multi_g, r_end_g = get_multi_regex('g')
    multi_grams = re.search(r_multi_g, name)

    r_multi_ml, r_end_ml = get_multi_regex('ml')
    multi_ml = re.search(r_multi_ml, name)

    r_multi_l, r_end_l = get_multi_regex('l')
    multi_l = re.search(r_multi_l, name)

    r_g = get_single_regex('g')
    grams = re.search(r_g, name)

    r_ml = get_single_regex('ml')
    ml = re.search(r_ml, name)

    r_kg = get_single_regex('kg')
    kg = re.search(r_kg, name)

    r_l = get_single_regex('l')
    l = re.search(r_l, name)

    r_cl = get_single_regex('cl')
    cl = re.search(r_cl, name)

    if multi_grams:
        set_weight(product, re.search(r_end_g, name))
        continue

    elif multi_ml:
        set_weight(product, re.search(r_end_ml, name))
        continue

    elif multi_l:
        set_weight(product, re.search(r_end_l, name), 1000)
        continue

    elif grams:
        set_weight(product, grams)
        continue

    elif ml:
        set_weight(product, ml)
        continue

    elif kg:
        set_weight(product, kg, 1000)
        continue

    elif l:
        set_weight(product, l, 1000)
        continue

    elif cl:
        set_weight(product, cl, 10)
        continue

    else:
        print('cant parse:', product.sainsburys_id, product.name)
