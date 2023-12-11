import pyperclip
with open("products_scraped.json", "r") as f:
    string = f.read()
products = string.split('""')
product_string = ",\n".join(products)

pyperclip.copy(product_string)
