# supermarket-search

this is a project to scrape the products from sainsburys.co.uk and get their price, weight and nutritional info. This is then used to calculate the products with the most sugar per £1

## setup
1. To scrape the products run `scrape.py`, this takes a while leaving 1s between products as otherwise you get blocked from the website. Currently there are 17,475 products that can be collected from the sitemap
2. To parse the prices out of the titles run `parse_weights.py`
3. To get the list of products ordered by most sugar per £1 run `search.py`, you can customise the query to work out other information about the products you might want to know

happy searching :)
