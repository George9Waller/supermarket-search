weight_in_g = float(input('Enter weight in grams: '))
sugar_per_100g = float(input('Enter sugar per 100g: '))
price = float(input('Enter price in £ e.g. 1.25: '))

g_per_money = ((weight_in_g / 100.0) * sugar_per_100g) / price

print(f'\n{g_per_money}g per £1')
