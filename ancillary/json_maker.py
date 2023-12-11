import json
import os
import sys


file_path = os.path.abspath(__file__)
dir_path = os.path.dirname(file_path)


products = {
    "vd": "Volt Delta",
    "exinda": "GFI - Exinda Network Orchestrator",
    "ssmart": "StreetSmart",
    "ffm": "Field Force Manager",
    "pb": "Playbooks",
    "bonzai": "Bonzai Intranet",
    "firstrain": "FirstRain",
    "lg": "GFI - LanGuard",
    "evmgr": "GFI - Eventsmanager",
    "xinet": "Northplains - Xinet",
    "kandy": "Kandy",
    "alp": "ALP",
    "kc": "Kayako Classic",
    "jvhop": "Jive HOP",
    "tnk": "Kayako",
    "streetsmart": "StreetSmart",
    "jvcld": "Jive Cloud",
    "mob": "Mobilogy Now",
    "cf": "Central Finance",
    "ans": "AnswerHub",
    "acrm": "CRM",
    "ev": "Everest",
    "bz": "Ignite BizOps", 
    "sky": "Skyvera Analytics",
    "sky5g": "Skyvera Network 5G & WiFi",
    "acorn": "Acorn",
    "l3" : "Learn and Earn",
    "error": "**[ProdSearchExcept](https://none)**",
    }

jira_links = {
    "itrel": "https://trilogy-eng.atlassian.net/browse/ITREL",
    "vd": "https://workstation-df.atlassian.net/browse/ZTPS-30562",
    "ev": "no Jira",
    "exinda": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EXOS/issues",
    "ssmart": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues",
    "ffm": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues", #StreetSmart link for FFM
    "pb": "https://trilogy-eng.atlassian.net/jira/software/c/projects/INSIDESALES/issues", # Playbooks is INSIDESALES
    "bonzai": "https://trilogy-eng.atlassian.net/jira/software/c/projects/BONZAI/issues",
    "firstrain": "https://trilogy-eng.atlassian.net/jira/software/c/projects/FIRSTRAIN/issues",
    "lg": "https://trilogy-eng.atlassian.net/jira/software/c/projects/GFIL/issues",
    "xinet": "https://trilogy-eng.atlassian.net/jira/software/c/projects/XINET/issues",
    "kandy": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KANDY/issues",
    "alp": "https://trilogy-eng.atlassian.net/jira/software/c/projects/ALP/issues",
    "kc": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KAYAKOC/issues",
    "jvcld": "https://trilogy-eng.atlassian.net/jira/software/c/projects/JVCLD/issues",
    "jvhop": "https://trilogy-eng.atlassian.net/jira/software/c/projects/JVHOPST/issues",
    "streetsmart": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues",
    "mob": "https://trilogy-eng.atlassian.net/jira/software/c/projects/MOBILOGY/issues",
    "evmgr": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EVENTSMGR/issues",
    "acorn": "https://workstation-df.atlassian.net/browse/IBUENG/issues",
    "cf": "https://workstation-df.atlassian.net/jira/core/projects/CFIN/issues",
    "ans": "https://trilogy-eng.atlassian.net/jira/software/c/projects/ANSWER/issues",
    "acrm": "https://trilogy-eng.atlassian.net/jira/software/c/projects/CRM/issues",
    "tnk": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KAYAKO/issues",
    "bz": "https://workstation-df.atlassian.net/jira/core/projects/IGBIZOPS/issues",
    "ztps": "https://workstation-df.atlassian.net/jira/core/projects/ZTPS/issues",
    "sky": "no Jira",
    "sky5g": "no Jira",
    "l3" : "no Jira",
    }


#small check
flag_jira = False
flag_prod = False
for key in jira_links:
    if key not in ["itrel", "ztps"]:
        if key not in products:
            print("key: " + key + " not in products")
            flag_jira = True
        
for key in products:
    if key not in ["error"]:
        if key not in jira_links:
            print("key: " + key + " not in jira_links")
            flag_prod = True

if flag_jira:
    print("Products are missing")
if flag_prod:
    print("Jira links are missing")
if flag_jira or flag_prod:
    print("Exiting...")
    sys.exit(1)
#Small check end

with open(os.path.join(dir_path, "products.json"), "w") as outfile:
    json.dump(products, outfile, indent=4)

with open(os.path.join(dir_path, "jira_links.json"), "w") as outfile:
    json.dump(jira_links, outfile, indent=4)
    print("Done")
    sys.exit(1)


