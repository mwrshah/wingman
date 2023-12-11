import json
import os
import sys

file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)

with open(os.path.join(dir_path, 'jira_links.json'),'r') as f:
    products_dict = json.load(f)


for key, value in products_dict.items():
    print(f"{key} : {value}")


