import pyperclip
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import textwrap
import shutil
import sys
import os
import json


file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)


def get_product(soup):
        all_labels = soup.find_all('label',{'class':'sc-anv20o-4 iIWDoF StyledLabel-sc-2utmsz-0 bYrRLL'})
        prod_name = "**[ProdSearchExcept](https://none)**"
        for label in all_labels:
            if label.text.find("Product*") != -1:
                prod_name = label.find_next('div', {'class': 'StyledEllipsis-sc-1u4uqmy-0 gxcmGf'}).text
                prod_name = prod_name.strip()
                break
        return prod_name


#####WIP
def main():
    qt = False
    while qt == False:
        html_content = None
        soup = None
        target_div = None
        ticket_soup = None

        html_content = pyperclip.paste()
        if html_content == None:
            html_content = "Nothing"
        if html_content.startswith("<html"):
            soup = BeautifulSoup(html_content, 'html.parser')
            target_div = soup.find("div", {"class": "ticket-panes-grid-layout active sc-9rzm4f-0 cusuqB"}) 
            ticket_soup = soup.find("div", {"class": "sc-lzuyri-0 gOXeKF"})
            if target_div:
                soup = target_div
        else:
            print_bright("No HTML content found in clipboard. Please copy a Zendesk ticket or chat conversation and try again.",bredf)
            soup = BeautifulSoup("<html></html>", 'html.parser')
            f_pr = ""
            conversation = ""

        prod_name = get_product(soup)
        with open(os.path.join(dir_path, "products_scraped.json"), "a") as outfile:
            json.dump(prod_name, outfile, indent=4)
            print(f"Product name added:{prod_name}")
        
        qt = input("Quit? (y/n): ")
        if qt == "y":
            qt = True 
        else:
            qt = False
            continue

main()
  
