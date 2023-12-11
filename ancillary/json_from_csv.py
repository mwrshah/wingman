import json
import os
import sys
import pandas as pd
import pyperclip


pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)


file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)

filename = input()
filename = filename+".csv"
with open(os.path.join(dir_path, filename), "r") as f:
    df = pd.read_csv(f)

#define a function to combine two columns with some string in between
def combine(row):
    return '"' + row['Key'] + '"' + ': ["'+ row['SaaS Jira Link'] + '", "'+ row['BU Jira Link'] + '" ],'
#clean up dataframe by replacing floats / nan with empty string
df = df.fillna('no jira')
#apply the function to each row of the dataframe
df['combined'] = df.apply(combine, axis=1)
#copy the result to clipboard
pyperclip.copy(df['combined'].to_string(index=False))

##small check
#flag_jira = False
#flag_prod = False
#for key in jira_links:
#    if key not in ["itrel", "ztps"]:
#        if key not in products:
#            print("key: " + key + " not in products")
#            flag_jira = True
#        
#for key in products:
#    if key not in ["error"]:
#        if key not in jira_links:
#            print("key: " + key + " not in jira_links")
#            flag_prod = True
#
#if flag_jira:
#    print("Products are missing")
#if flag_prod:
#    print("Jira links are missing")
#if flag_jira or flag_prod:
#    print("Exiting...")
#    sys.exit(1)
##Small check end
#
#with open(os.path.join(dir_path, "products.json"), "w") as outfile:
#    json.dump(products, outfile, indent=4)
#
#with open(os.path.join(dir_path, "jira_links.json"), "w") as outfile:
#    json.dump(jira_links, outfile, indent=4)
#    print("Done")
#    sys.exit(1)
#
#
