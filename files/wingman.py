##A scripting tool
import re
import copy
import pyperclip
from openai import OpenAI
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import textwrap
import shutil
import sys
import os
import json
import platform #Used for clear only
import time
import configparser
import yaml
import hidden_key
#Import submodules from the same directory
from html_walk import get_zd_messages, get_first_pr 
from printing_funk import *
import hidden_key

#javascript:(function() { var htmlContent = document.documentElement.outerHTML; navigator.clipboard.writeText(htmlContent); })();


#Find the path where the script is running 
# to default to config bundled with the executable
def get_resource_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        print("Error: Could not find the resource path in sys._MEIPASS.")
        base_path = os.path.join(os.path.expanduser("~"), "Documents", "wingman")
    return base_path

#Get the files from the users documents directory
dir_path = os.path.join(get_resource_path(),"appdata")
set_dir_path = os.path.join(os.path.expanduser("~"), "Documents", "wingman","appdata")

if not dir_path:
#python script defined path - non executable
    try:
        dir_path = set_dir_path
        print("dir_path is set to ~/Documents/wingman/appdata")
#windows executable - defined path in runbook to place config
    except Exception:
        print("Error: Could not find the resource path in fallback ~/Documents/wingman/appdata.")
        dir_path = os.path.abspath(".")

config = configparser.ConfigParser()
try:
    config.read(os.path.join(set_dir_path, 'config.ini'))
except Exception as e:
    print("Error: Could not read the config.ini file.")
    print(e)
#get the agent name
try:
    agent_name = config['User']['name']
except KeyError:
    agent_name = "John Doe"

#get the gpt model for escalations
try:
    esc_model_value = config['Models']['esc_model']  
    if "gpt-4-turbo" in esc_model_value:
        esc_model = "gpt-4-1106-preview"
    elif "gpt-4" in pr_model_value:  
        esc_model = "gpt-4"
except KeyError:
    esc_model = "gpt-4-1106-preview"

#get the gpt model for prs
try:
    pr_model_value = config['Models']['pr_model']  
    if "gpt-4-turbo" in pr_model_value:
        pr_model = "gpt-4-1106-preview"
    elif "gpt-4" in pr_model_value:
        pr_model = "gpt-4"
except KeyError:
    pr_model = "gpt-4"


#Fileload products and their jira links from json files

try:
    with open(os.path.join(set_dir_path, 'products_to_jiras.json'),'r') as f:
        products_to_jiras = json.load(f)
except json.JSONDecodeError:
    print("The products_to_jiras.json file is corrupted or invalid.")
except FileNotFoundError:
    print("The products_to_jiras.json file is missing.")
except Exception as e:
    print("An error occured while loading the products_to_jiras.json file.")
    print(e)

try:
    with open(os.path.join(set_dir_path, 'saas_jira_links.json'),'r') as f:
        saas_jira_links = json.load(f)
except json.JSONDecodeError:
    print("The saas_jira_links.json file is corrupted or invalid.")
except FileNotFoundError:
    print("The saas_jira_links.json file is missing.")
except Exception as e:
    print("An error occured while loading the jira_links.json file.")
    print(e)


try:
    with open(os.path.join(set_dir_path, 'bu_jira_links.json'),'r') as f:
        bu_jira_links = json.load(f)
except json.JSONDecodeError:
    print("The bu_jira_links.json file is corrupted or invalid.")
except FileNotFoundError:
    print("The bu_jira_links.json file is missing.")
except Exception as e:
    print("An error occured while loading the jira_links.json file.")
    print(e)

#get the api key
try:
    with open(os.path.join(dir_path, 'hidden_key.txt'),'r') as f:
        api_key = f.read().strip()
except FileNotFoundError:
    print("The hidden_key.txt file is missing.")
except Exception as e:
    print("An error occured while loading the hidden_key.txt file.")
    print(e)

if not api_key:
    try:
        with open(os.path.join(set_dir_path, 'hidden_key.txt'),'r') as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("The hidden_key.txt file was not found in ~/Documents/wingman/appdata.")

if not api_key:
    try:
        api_key = hidden_key.api_key
    except AttributeError:
        print("The api_key was not found in hidden_key.py")

os.environ["OPENAI_API_KEY"]= api_key

#get the prompts
try: 
    with open(os.path.join(set_dir_path, 'prompts.yaml'),'r') as f:
        prompts = yaml.safe_load(f)
except FileNotFoundError:
    print("The prompts.yaml file is missing.")
except Exception as e:
    print("An error occured while loading the prompts.yaml file.")
    print(e)



#Global scope vars for printing
terminal_width = shutil.get_terminal_size().columns
chrt = "|" #· ⋮
subindent = " "+chrt+" "
available_width = terminal_width - len(subindent)



#FLOW and changes - define an intent in the following
#1. Add search term and new intent to the intent_sets dictionary
#2. Add search term to ancilliary intents that might apply such as bu_jira, saas, sc etc.
#2. Add the scenario_subsets that apply to scenario_subsets dict
#3. Add changes like mhteam and jirabiz to the mapping_one_to_one dictionary
#4. Add jira with the intent_name?? WIP

negations = ["ont", "not", "n't", "no", "minus", "excluding", "without"]

intent_sets = {}
insertion = {}

#Loading Jira keys to intent_sets as a separate intent
staging_list_saas = [] #for_load_to_scenario_subsets
for key, value in saas_jira_links.items():
    insertion[key] = [" " + key.lower() + " "]
    staging_list_saas.append(key) 

staging_list_bu = [] #for_load_to_scenario_subsets
for key, value in bu_jira_links.items():
    insertion[key] = [" " + key.lower() + " "]
    staging_list_bu.append(key)
intent_sets.update(insertion)



insertion = {
        "restart" : [" reload ~", " refresh ~"," restart ~", " redo ~", " re ~" ], #if entire value is this is implied by starting space and the ending char ~
        "quit" : ["quit ~", "exit ~"," qiut ~", "qitu ~", "guti ~", "exti ~" ],
        "cls" : ["close", "cls"],
        "cst" : ["send to customer", "send to cust", "customer", "cust", "cst"],
        "l1" : ["task", "tsk", " l1 ", "level 1", "level one", "l1n"],
        "l2" : [" l2 ", "level 2", "level two", "l2n"],
        "esc" : ["escalat", "elevat", " exn ", " excf ", " exsc ", 
                 "send an ", "external", "escalate", "elevate", " ext ", " esc ", 
                 "send this to","send it to", "send to", "send via", "send through"],
        }
intent_sets.update(insertion)

intent_sets["no_esc"] = [x+" "+ y.strip() for x in negations for y in intent_sets["esc"]]

insertion = {
        "yes_pr" : [" a pr ", "prepare a pub", "prepare a pr", " pr ", "write a p", "draft a p", "make p", "make a pub", "make a pr ",
                    "compose", "yes pr", "send a p", "public resp", "send a public" ],
        "no_pr" : ["no pr", "don\'t write", "no reply", "no response", "don\'t draft","don\'t draft",
                   " exn ", "l2n", "don\'t send a pr", "n\'t write a pr", "dont send a pr",
                    "dont write a pr", "don\'t prepare a pr", "dont prepare a pr"
                   "without pr", "excluding pr", "minus pr"], 
        }
intent_sets.update(insertion)

intent_sets["no_pr"] += [x+" "+ y.strip() for x in negations for y in intent_sets["yes_pr"]]

insertion = {
        "sum" : ["summarize", " summ", " smrz ", " sumri ",  " smri",  "summary", " sumr "," sumz ", " smz ", " smry " ],
        "ext" : ["external to esw", "ext to esw",],
        "vp" : [" vp "],
        "cf" : [" credit memo ", " cfin ", "to finance"," the finan", " fin ","cf ", "central finance", "treasury", " ap ", "collect cash", "udf", "accounts pay", " rishap", "cquery", "write off", "vendor reg", "vendor pay", "o2c", "record maint", "record mn", "record man", "record mg"],
        "cf_csquery" : ["csquery", "rishap"], 
        "cf_udf" : [" udf "],
        "cf_ap" : [" ap ", "accounts pay"],
        "cf_writeoff" : ["write off", "writeoff", "write-off"],
        "cf_creditnote" : ["credit note"],
        "cf_vendorreg" : ["vendor reg"],
        "cf_vendorpay" : ["vendor pay", "treasury"],
        "cf_o2c" : [" o2c ","record maint", "record man"],
        "cf_tax" : ["tax team"],
        "cf_treasury" : ["treasury team", " edgar "],
        "cf_generic" : ["collect cash", " cf ", " central fin", "finance" ],
        "cf_wsf" : [" wsf "],
        "alpha_lang" : ["alpha lang", "language"],
        "sc" : [ " sc ","side conv", "side conversation", " ex ",],
        "bz" : [" bz ", "business ops", "bizops ", "exbz",],
        "bu_jira" : [ " bu jira ", "ibueng", "ignite bu eng", "itpef", "ztps", "business ops", " bz ", "bizops", "exbz",],
        "jira_generic" : ["on jira", " jira ", " jra ", " jir ", " jirn ", " jiran",],
        "acc_mgt" : [" acct ", " acc ", "account management", "account manager", " am ", " accm ", " accmg ", " accman ", " accmn ", " accmgt "],
        "eng" : [" eng ", "engineer", "engineering", "exeng", "exengn"],
        "bu" : [ "exbn", "noc ", " elvt ", " bu ", "exb"], 
        "force_esc" : ["send sc", "send an sc", "bu jira","via esc", "through esc", "by esc", "on esc", 
                       "over jira", "on jira", "on sc ", "over sc", 
                       "on side", "through jira", "via jira", "via side", "via sc", "by sending an sc",
                       "not by elevating", "not via elev", "not through elev", "not on elev", "not over elev",],
        }
intent_sets.update(insertion)

intent_sets["bu_jira"] += [x+" "+ "jira" for x in intent_sets["bu"]]
intent_sets["bu_jira"] += [x+" "+ "via jira" for x in intent_sets["bu"]]

intent_sets["force_elevate"] = ["send to bu", "elevation to", "elevate to bu", "elevate to the bu", "bu elevation", "via elev", 
                           "to the bu", "send to the bu", "through elev", "by elev", "on elev", "over elev", 
                           "not on jira", "not through jira", "not via jira", "not on sc", 
                           "not through sc", "not via esc", "not through esc", "not on esc",
                           "not via side", "not through side", "not on side", "not via elev",
                            "not through elev", "not on elev", "not over elev", "not by elev",
                            "not by sending an sc", "not by sending a sc", "not by sending a side",]

intent_sets["force_esc"] += [x+" "+ y.strip() for x in negations for y in intent_sets["force_elevate"]]

insertion = {        
        "chat": ["clschn","clsch"," chat ", " cht ",],
        "clst" : ["ticket", " tkt ", " tckt ","clst"],
        "saas" : [" saas ", " infra t", " infrastructure t", " exsaas "],
        "incident" : [" inc","incident", "incdt"],
        "chg_req" : ["change request", "chng req", "chg req", "chngreq"],
        "in_esc_update" : [item for item in intent_sets["no_esc"]] + ["back on hold", "in escalation", "in esc ", "pending input",
                                                                      "waiting", "exold","pending on", "pending with", 
                                                                      "pending over", "update requester", "update cust" ],
        "ibueng" : ["ignite bu eng", "ibueng"],
        "itpef" : ["feature req", "itpef"],
        "ztps" : ["ztps", " ps jira" ],
        "itrel" : ["itrel"],
    }
intent_sets.update(insertion)
# Load jira keys to saas and bu jira scenarios
for item in staging_list_saas:
    intent_sets["saas"] += [" " + item.lower() + " "]
for item in staging_list_bu:
    if item not in ["CFIN"]:
        intent_sets["bu_jira"] += [" " + item.lower() + " "]


half_list = ["l1", "cst", "exsc", "exold", "ex", "exjira", "exeng", "exb", "l2", "clst", "clsch", "sum"] 
full_list = half_list + [item+"n" for item in half_list]

scenario_subsets= {
            "restart"       :["restart"],
            "quit"          :["quit"],
            "cls"           :["clst", "clstn", "clsch","clschn"],
            "cst"           :["cst", "cstn"],
            "l1"            : ["l1n"],
            "l2"            : ["l2", "l2n"],
            "esc"           :[item for item in full_list if item.startswith("e") and not item.startswith("exold")] 
                                + ["l2", "l2n", "l1","l1n"],
            "no_esc"        : [item for item in full_list if item not in ["exjira","exjiran","exsc", "exscn"]], 
            "yes_pr"        : list(filter(lambda x: x not in ["clsch"], half_list)), 
            "no_pr"         :[ "tsk",]+[item for item in full_list if item.endswith("n")],
            "sum"           :["sum"],
            "ext"           :["exsc", "exscn", "exold", "exoldn"],
            "vp"            :["exsc","exscn","exold","exoldn"],
            "cf"            :["exjira", "exjiran", "exold", "exoldn"],
            "cf_csquery"    :["exjira", "exjiran","exold","exoldn"], 
            "cf_udf"        :["exjira", "exjiran","exold","exoldn"],
            "cf_ap"         :["exjira", "exjiran","exold","exoldn"],
            "cf_writeoff"   :["exjira", "exjiran","exold","exoldn"],
            "cf_creditnote" :["exjira", "exjiran","exold","exoldn"],
            "cf_vendorreg"  :["exjira", "exjiran","exold","exoldn"],
            "cf_vendorpay"  :["exjira", "exjiran","exold","exoldn"],
            "cf_o2c"        :["exjira", "exjiran","exold","exoldn"],
            "cf_tax"        :["exjira", "exjiran","exold","exoldn"],
            "cf_treasury"   :["exjira", "exjiran","exold","exoldn"],
            "cf_generic"    :["exjira", "exjiran","exold","exoldn"],
            "cf_wsf"        :["exjira", "exjiran","exold","exoldn"],
            "alpha_lang"    :["exalpha","exalphan"],
            "sc"            :["exsc", "exscn","exold","exoldn"],
            "bz"            :["exjira", "exjiran","exold","exoldn"],
            "bu_jira"       :["exjira", "exjiran","exold","exoldn"],
            "jira_generic"  :["exjira", "exjiran","exold","exoldn"],
            "acc_mgt"       :["exsc", "exscn","exjira", "exjiran","exold","exoldn"],
            "eng"           :["exeng", "exengn","exold","exoldn"],
            "bu"            :["exb","exbn",],
            "force_esc"     :[item for item in full_list if item not in ["exb", "exbn"]],
            "force_elevate" :[item for item in full_list if item not in ["exsc", "exscn","exjira","exjiran"]],
            "chat"          :["clschn"],
            "clst"          :["clst","clstn"],
            "saas"          :["exjira", "exjiran","exold","exoldn"],
            "incident"      :["exjira", "exjiran","exold","exoldn"],
            "chg_req"       :["exjira", "exjiran","exold","exoldn"],
            "in_esc_update": ["exold", "exoldn"],
            "ibueng"        :["exjira", "exjiran","exold","exoldn"],
            "itpef"         :["exjira", "exjiran","exold","exoldn"],
            "ztps"          :["exjira", "exjiran","exold","exoldn"],
            "itrel"         :["exjira", "exjiran","exold","exoldn"],
    }

#Load jira keys to scenario_subsets
for item in staging_list_saas+staging_list_bu:
    scenario_subsets[item] = ["exjira", "exjiran","exold","exoldn"]


#Smallcheck
scenario_subsets_keys = set(scenario_subsets.keys())
intent_sets_keys = set(intent_sets.keys())
if scenario_subsets_keys != intent_sets_keys:
    diff1 = list(scenario_subsets_keys - intent_sets_keys)
    diff2 = list(intent_sets_keys_set - scenario_subsets_keys_set)
    diff = diff1 + diff2
    print(repr(diff))
    print("Error: Scenario subsets and intent sets do not match"*20)  
#Smallcheck end

#print(scenario_subsets["no_pr"]) #debug
global_intents_list = []
for key, value in intent_sets.items():
    global_intents_list.append(key)

#defining functions


def get_ticket_number(ticket_soup):
    ticketnumber = "**[TicketSearchExcept](https://none)**"
    if ticket_soup is not None:
        ticketnumber = str(ticket_soup.get("data-entity-id"))
    return ticketnumber

def get_product(soup):
        all_labels = soup.find_all('label',{'class':'sc-anv20o-4 iIWDoF StyledLabel-sc-2utmsz-0 bYrRLL'})
        prod_name = "**[ProdSearchExcept](https://none)**"
        for label in all_labels:
            if label.text.find("Product*") != -1:
                prod_name = label.find_next('div', {'class': 'StyledEllipsis-sc-1u4uqmy-0 gxcmGf'}).text
                prod_name = prod_name.strip()
                break
        if prod_name == "EDU":
            prod_name = "Alpha"
        return prod_name

def scenario_extractor(instruction_string):
    
    #TAPE - The program used to work by splitting a single input into instruction and clue. Changing that to separate inputs.
    def pbug(name,value):
        print("Printing "+name+ ": "+value+"\n")
        return None

    collected_intents_dict = {} #COLLECTION OF ALL INTENTS FOUND
   

    input_string = " " + instruction_string + " ~" 
    parse_string_full = input_string.lower()
    parse_string = parse_string_full[:300]
    last_dot_idx = parse_string.rfind(".")
    if last_dot_idx != -1: #skip the last dot
        parse_string = parse_string[:last_dot_idx] + " " + parse_string[last_dot_idx+1:]
    parse_string = parse_string.strip()
    #pbug("parse_string",parse_string) #debug
    
    gt_idx1 = parse_string.find("sdfsdfsdfdxas") #TAPE - hobbled it
    
    mark_idx1 = parse_string.find("`")
    
    #if both found
    if gt_idx1 != -1:
        gt_present = True
        end_idx1 = gt_idx1
    elif mark_idx1 != -1:
        mark_present = True
        end_idx1 = mark_idx1
    else:
        end_idx1 = 300 #TAPE - used to be - 80 is a random number for slicing 80% of the parse string.


    slice1 = parse_string[:end_idx1]
     
    slice1 = " " + slice1 + " " #some of the search terms are defined with leading spaces so this is necessary for search term starting at the beginning of the sentence. The benefit of having space in the search term is it won't fire for term appearing within a word. Example " sc "
    slice1 = slice1.replace("`", " `")
       #slice one gets passed on 

    #1 - Send to customer 
    #2 - Close ticket - with a PR
    #3 - Place back on hold - with a PR
    #4 - Send to external team (via Side Conversation)
    #5 - Send to external team (SaaS Incident)
    #6 - Send to external team (SaaS Change Request)
    #7 - Send to external team (Engineering)
    #8 - Send to external team (BU Jira)
    #9 - Send to external team (CFIN)
    #10 - Send to L1 - no PR
    #11 - Send to L2 - with a PR
    #12 - Elevate to BU - with a PR 
    #13 - Summarize chat


        #fixed scenarios
    slice1 = slice1.replace("alt" ," no pr")
    slice1 = slice1.replace(" 1 " ," send to cust ")
    slice1 = slice1.replace(" 2 " ," close ticket ") 
    slice1 = slice1.replace(" 3 " ," send in esc ")
    slice1 = slice1.replace(" 4 " ," send an sc ") 
    slice1 = slice1.replace(" 5 " ," send to saas ")
    slice1 = slice1.replace(" 6 " ," send to saas chg req ")
    slice1 = slice1.replace(" 7 " ," send to eng ")
    slice1 = slice1.replace(" 8 " ," send to bu jira ")
    slice1 = slice1.replace(" 9 " ," send to cf ")
    slice1 = slice1.replace(" 10 " ," send to l1 no pr ")
    slice1 = slice1.replace(" 11 "," send to l2 ")
    slice1 = slice1.replace(" 12 "," send to bu ")
    slice1 = slice1.replace(" 13 "," sumz ")
    slice1 = slice1.replace(" 14 "," close chat ")
    def negation_check(string):
        string = string.strip()
        idx_space = string.rfind(" ")
        if idx_space!= -1:
            string = string.replace(" ", "                     ")
        if any(string[-13:].find(word) != -1 for word in negations):
            return True
        else:
            return False


    encapsulated_terms = []
    #Small check on inclusion of one search term in another
    def encapsulated_check(term1, term2):
        if term1 in term2 and len(term1) < len(term2):
            #print(f"Warning: {term1} is encapsulated in {term2}.")
            return True
        else:
            return False
   
    #intent extractor collects the intents that match in the parsed string and stores them in a collected_intents_dict
    def intent_extractor(string, intent_sets_dict):
        if not string:
            return None
        string = string.replace("’","'") #What a trip it has been figuring this out
        for intent, searchtermlist in intent_sets_dict.items():
            for searchterm in searchtermlist: 
                where_is_it = string.find(searchterm) 
                if where_is_it != -1: 
                    new_string = string[where_is_it-15:where_is_it]
                    if not negation_check(new_string):
                        searchterm = searchterm
                        found_intent = intent  
                        existing_encapsulated_searchterm = False
                        for term, val in collected_intents_dict.items():
                            if encapsulated_check(searchterm, term):
                                existing_encapsulated_searchterm = True 
                                break
                        if not existing_encapsulated_searchterm:
                            if searchterm not in collected_intents_dict.keys():
                                collected_intents_dict[searchterm] = found_intent
                            else:
                                collected_intents_dict[searchterm+found_intent] = found_intent  #I want to be able to process
                                                                                                #multiple intents based on a common
                                                                                                #search term. That's what the approach
                                                                                                #of getting an intersection set is
                                                                                                #predicated on. So Collected intents 
                                                                                                #should have been a list of tuples to 
                                                                                                #allow duplicate keys. But I didn't, 
                                                                                                #so I'm using a hacky solution.



        return None
    
    intent_extractor(slice1,intent_sets) 
    tempintentionsets_list = []
    unique_intents_list = []
    unique_intents = set() 
    
    for searchterm, intent in collected_intents_dict.items():
        unique_intents.add(intent)
   
    def intent_popper(unique_intents, over_riding_intent, pop_list):
        if over_riding_intent in unique_intents and any(item in unique_intents for item in pop_list):
            for item in pop_list:
                unique_intents.discard(item) 
        return None 
 
    #OVERRIDES 
    intent_popper(unique_intents, "no_pr",["yes_pr"])
    intent_popper(unique_intents, "no_esc",["esc"])
    intent_popper(unique_intents,"saas",["jira_generic","bu_jira"])
    intent_popper(unique_intents, "sum",["chat"])
    intent_popper(unique_intents, "sc", ["saas","jira_generic","bu_jira"])
    intent_popper(unique_intents, "in_esc_update", ["esc"])
    intent_popper(unique_intents, "bu_jira", ["bu","force_elevate"])
    intent_popper(unique_intents, "force_esc", ["force_elevate", "no_esc", "bu"])
    intent_popper(unique_intents, "force_elevate", ["esc", "in_esc_update"])
    
    cf_gen_overrides =( "cf_csquery", "cf_udf", "cf_ap", "cf_writeoff", "cf_vendorreg", "cf_vendorpay", 
                       "cf_o2c", "cf_tax", "cf_treasury", "cf_wsf")
    for scenario in cf_gen_overrides:
        intent_popper(unique_intents, scenario,["cf_generic"])

    intent_popper(unique_intents, "cf", ["force_esc", "force_elevate"])
    


    unique_intents_list = list(unique_intents) #List for passthrought
    #FETCH SUBSET OF FORMS
    for intent in unique_intents:
        intent_subset = set(scenario_subsets[intent])
        tempintentionsets_list.append(intent_subset) 
    
#returns true only if there is one intentionset with only one form in it

    def single_value_checker():
        oneitemcount = 0
        #twoitemcount = 0
        oneflag = False
        #twoflag = False
        for item in tempintentionsets_list:
            if len(item) == 1:
                oneitemcount += 1
                if oneitemcount > 1:
                    oneflag = False
                else:
                    oneflag = True
            #elif len(item) == 2:
             #   twoitemcount += 1
              #  if twoitemcount > 1:
               #     twoflag = False
                #else:
                #    twoflag = True
                 #   itemtocheck = item
        if oneflag == True:
            return True

        #if twoflag == True:
         #   if any(subitem.endswith("n") for subitem in itemtocheck):
          #      return True
           # else:
            #    return False
        
#venn intersection happening here. Lookuplist will end up with something /form
    lookuplist = [] 
    info_print = term_print_string("Intersection set is empty","  ")
    if tempintentionsets_list:
        #multi value scenario
        if not single_value_checker():
            intersectionset = tempintentionsets_list[0]
            if len(tempintentionsets_list) > 1:
                for current_set in tempintentionsets_list[1:]:
                    intersectionset &= current_set
                    if len(intersectionset) == 0:
                        print_bright(info_print,bredf)
                        lookuplist = list(min(tempintentionsets_list, key=len))
                    else:
                        lookuplist = list(intersectionset)
            else:
                lookuplist = list(tempintentionsets_list[0])
        #single value scenario
        elif any(item for item in tempintentionsets_list if len(item) ==1): 
            targetset = next((item for item in tempintentionsets_list if len(item)==1), None)
            lookuplist = list(targetset)
       
        #else should never fire based on logic in single_value_checker
        else:
            intersectionset = tempintentionsets_list[0]
            for current_set in tempintentionsets_list[1:]:
                intersectionset &= current_set
                if len(intersectionset) == 0:
                    print_bright(info_print,bredf) 
                    lookuplist = list(min(tempintentionsets_list, key=len))
                else:
                    lookuplist = list(intersectionset)
    else:
    #No input - no intents found
        lookuplist = []
    
    
    intents_joined_from_list_trash = ", ".join(unique_intents_list)
    flowbreak1 = "\nWingman couldn't decide which output you want.\n\n*  Try to eliminate the contradictory option.\n\n*  Add more detail.'acct mgr sc no pr' needs 'escalate to' before it.\n\n*  if you said 'elevate' try escalate instead. \n\n*  instead of 'send to external team' try 'escalate to saas change req'" 
    extrainfo = f"{yellowf}Parsed intents:{resetf}"+" "f"{bcyanf}{intents_joined_from_list_trash}{resetf}"
    flowbreak2 = "\nWingman is confused about what you want to do.\
Try being more specific." 

    wrapped_flowbreak1 = term_print_string(flowbreak1,"   ")
    wrapped_flowbreak2 = term_print_string(flowbreak2,"   ")
    if len(lookuplist) == 0:
        print_bright(wrapped_flowbreak2,greenf)     
        print(extrainfo)
        print(f"{yellowf}Possibilities list: {resetf} " + f"{bredf}{str(lookuplist)}{resetf}")
    elif len(lookuplist) > 1:
        #EXTREME TAPE - to make it default to sc if no intersection found
        if set(lookuplist) == set(["exjiran","exscn"]):
            lookuplist = ["exscn"]
        elif set(lookuplist) == set(["exjira","exsc"]):
            lookuplist = ["exsc"]
        else:
            old_lookuplist = lookuplist.copy()
            lookuplist = [scenario for scenario in lookuplist if not scenario.endswith("n")]
            if len(lookuplist) > 1:
                print_bright(wrapped_flowbreak1,greenf)
                print(extrainfo)
                print(f"{yellowf}Possibilities list: {resetf} " + f"{bredf}{str(lookuplist)}{resetf}")
            elif len(lookuplist) < 1:
                print_bright(wrapped_flowbreak1+"\n\n ERROR:no_pr sets present in tandem",greenf)
                print(extrainfo)
                print(f"{yellowf}Possibilities list: {resetf} " + f"{bredf}{str(old_lookuplist)}{resetf}")

    if len(lookuplist) > 1:
        return None, None #TAPE - took out clue as an output for 2step

    elif len(lookuplist) == 0:
        return None, None #TAPE - took out clue as an output for 2step

    elif len(lookuplist) == 1:
        form_choice = lookuplist[0] 
        scenarioinfo_label = "Form:"
        scenarioinfo_print = form_choice
        if form_choice not in ["restart","quit"]:
            print()
            print(f"{yellowf}{scenarioinfo_label}{resetf}"+" "f"{bredf}{scenarioinfo_print}{resetf}")
            print("------------")
            intentinfo_label = "Parsed intents:"  
            intentinfo_print = str(unique_intents_list).replace("'","").replace("[","").replace("]","")
            print(f"{yellowf}{intentinfo_label}{resetf}"+" "f"{bcyanf}{intentinfo_print}{resetf}")
        return form_choice, unique_intents_list #TAPE - took out clue as an output for 2step


def ds_printer(finalstring):
    idx_link_end = finalstring.find("2jr)_\n")
    if idx_link_end != -1:
        idx_link_end += len("2jr)_\n")+1
        finalstring_sub = finalstring[idx_link_end:-1]
    else:
        finalstring_sub = finalstring
    finalstring_sub = finalstring_sub.replace("(https://none)","").replace("[","<").replace("]",">")
    finalstring_sub = finalstring_sub.replace("**","").replace("&nbsp;","").replace("  "," ")
    finalstring_sub = bu_elevation_stripper(finalstring_sub)
    finalstring_sub = jira_link_stripper(finalstring_sub)
    finalstring_sub = finalstring_sub.replace("---","."*(terminal_width-4))
    finalstring_sub = finalstring_sub.replace("\n","[nl]")
    fs_sub_paras = finalstring_sub.split("[nl][nl]")
    fs_sub_paras_nlpreserve = []
    fs_sub_paras_clean = []
    for para in fs_sub_paras:
        para = para.replace("[nl]","\n[rl]") #remaining single lines preserved as [rl]
        split_paras = para.split("\n")
        for splitpara in split_paras:
            fs_sub_paras_nlpreserve.append(splitpara)
    if fs_sub_paras_nlpreserve[-1] == "":
        del fs_sub_paras_nlpreserve[-1] 
    if fs_sub_paras_nlpreserve[0] == "":
        del fs_sub_paras_nlpreserve[0]
    for para in fs_sub_paras_nlpreserve:
        wrapped_para = textwrap.fill(para, 
                                    width=terminal_width-1,
                                    initial_indent=u'\u2551'+" ",
                                     subsequent_indent=u'\u2551'+" ",
                                )
        fs_sub_paras_clean.append(wrapped_para)
    fs_sub_clean = "\n║ \n".join(fs_sub_paras_clean)
    fs_sub_clean = fs_sub_clean.replace("\n║ [rl]","")
    fs_sub_clean = fs_sub_clean.replace("[rl]","\n║ ")
    sep2 = u'\u2554'+u'\u2550'*(terminal_width-2)+u'\u2557'
    sep3 = u'\u255A'+u'\u2550'*(terminal_width-2)+u'\u255D'
    print_bright(sep2,magf)
    print_bright(fs_sub_clean,magf)
    print_bright(sep3,magf)

def jira_link_stripper(string):
    start_idx = string.find("[Jira link]")   
    end_idx = string.find("/issues)")
    if start_idx != -1 and end_idx != -1:
        start_idx = start_idx+len("[Jira link]") 
        end_idx = end_idx+len("/issues)")
        return string[:start_idx] + string[end_idx:] 
    else:
        return string

def bu_elevation_stripper(string):
    start_idx = string.find("<table")   
    end_idx = string.find("</table")
    if start_idx != -1 and end_idx != -1:
        start_idx = start_idx-1
        end_idx = end_idx+len("</table")+2
        alt_string = """
    Issue summary:
    Reproduction steps:
    Current behaviour:
    Expected behaviour:
    Troubleshooting steps:
    Reason for escalation (BU do?):
    Justification for escalation:""" 
        string_after = string[:start_idx] + alt_string + string[end_idx:] 
        return string_after

    else:
        return string


def append_identities(list_of_messages,names):
    requester = names["requester"]
    support_agents = names["support"]
    filtered_messages = [item for item in list_of_messages if item[0] not in["AI", "ATLAS"]]
    role_mapping = {name: '|Support Agent|' for name in support_agents}
    role_mapping.update({name: '|Requester|' for name in requester})
    names_and_messages = [[f">>{role_mapping.get(name,"")} {name}", message] for name, message in filtered_messages]
    split_frames = []

    def message_multiplier(names_msg_list, re_spacer):
        merge_stage = []
        for name, message in names_msg_list:
            split_messages = re.split(re_spacer, message)
            split_messages = list(reversed(split_messages))
            if len(split_messages) > 1:
                for i in range(1, len(split_messages)):
                    split_messages[i] = "#.#" + split_messages[i]
            for split_message in split_messages:
                piece = [name,split_message]
                merge_stage.append(piece)
        return merge_stage 
    from_pattern = r"From:"
    wrote_pattern = r"On [A-Z][a-z]{2}\b,?"
    names_and_messages = message_multiplier(names_and_messages, from_pattern)
    names_and_messages = message_multiplier(names_and_messages, wrote_pattern)
    mod_n_and_m = []
    for name, message in names_and_messages:
        if message.startswith("#.#"):
            sliver= message[:50]
            idx_at = sliver.find("@")
            if idx_at == -1:
                idx_at = sliver.find(">")
            if idx_at != -1:
                new_message = message[idx_at+1:]
                new_name = f">>|Someone| {message[3:idx_at]}"
            else:
                new_message = message[3:]
                new_name = f">>|Someone|"
            mod_n_and_m.append([new_name, new_message]) 
        else:
            mod_n_and_m.append([name, message])
    
    combined_list = [f"{label}:\n {message} \n-------\n" for label,message in mod_n_and_m]
    return combined_list 


def get_intuitSummary(list_of_messages):
    if len(list_of_messages) > 10:
        short_list = list_of_messages[:4] + list_of_messages[-6:]
    else:
        short_list = list_of_messages
    short_list_str = "\n".join(short_list)
    client = OpenAI()
    sys_prompt = "You are a secretary who directs staff on open tickets by clarifying next steps"
    user_prompt = ( "Look at the messages that are in chronological order."
                   "As a response:\n - in a single sentence summarize the request, and the crux of the matter "
                   "(based on specific information in the messages 'Issue:' "
                   " \n - if relevant, to bring an agent up to speed, in phrases, what has support already done "
                   "updated the customer on.'Actions taken:'"
                   "\n - in a single phrase what is the latest on the situation. Mention details 'Now:'"
                    f"\n---\nMessages: \n {short_list_str} \n---\n")
    the_issue = client.chat.completions.create(
            model = "gpt-3.5-turbo-1106",
            temperature = 0.4,
            messages = [
                {"role":"system","content": sys_prompt },
                {"role":"user","content": user_prompt },
                ]
            )
    string = str(the_issue.choices[0].message.content)
    issue_string = string 
    actions_string = ""
    now_string = ""
    idx_len = 0
    issue_idx = string.find("Issue:")
    idx_len = len("Issue:")
    if issue_idx == -1:
        issue_idx = string.find("Summary:")
        if issue_idx != -1:
            idx_len = len("Summary:") 
    if issue_idx == -1:
        issue_idx = string.find("Request:")
        if issue_idx != -1:
            idx_len = len("Request:")
    actions_idx = string.find("Actions taken:")
    now_idx = string.find("Now:")

    if issue_idx != -1 and actions_idx != -1:
        issue_string = string[(issue_idx+idx_len):actions_idx]
    if actions_idx != -1 and now_idx != -1:
        actions_string = string[actions_idx+len("Actions taken:"):now_idx]
    if now_idx != -1:
        now_string = string[now_idx+len("Now:"):]
    list_output = [issue_string, actions_string, now_string]
    return list_output

def get_intuitPR(model_input,conversation,seededclue,sys_prompt,pr_prompt):
    client = OpenAI()
    clue = seededclue
    completion = client.chat.completions.create(
        model=model_input,
        temperature=0.8,  
        messages=[
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": pr_prompt },
        {"role": "assistant", "content": "Ok. Provide the conversation and the suggested_reply."},
        {"role": "user", "content": "Conversation:\n" + conversation},
        {"role": "assistant", "content": "Ok. Provide the suggested_reply."},
        {"role": "user", "content": "suggested_reply:\n" + clue},
        ]
    )
    string = str(completion.choices[0].message.content)
    string = bylinestripper(string) 
    return string

def get_intuitIssue(model_input,conversation,response,sys_prompt):
    client = OpenAI()
    subject = client.chat.completions.create(
            model=model_input,
            temperature=0.8,
            messages=[
                {"role":"system","content": "You are a customer support agent routing customer issues to other teams"},
                {"role":"user","content":  "Look at the messages in conversation and the last response sent to the customer, then summarize the customer issue in a single line or very short para, retain specific information:\n" + conversation + "Response:" + response},
                ]
            )
    string = str(subject.choices[0].message.content)
    return string


#Its not nice that dict is getting written to directly for the prepesc2 key. TAPE
def get_intuitEsc(model_input,conversation,response,dictname,clue,sys_prompt,pr_prompt,esc_prompt):
    client = OpenAI()
    subject = client.chat.completions.create(
            model=model_input,
            temperature=0.8,
            messages=[
                {"role":"system","content": sys_prompt +"Sometimes have to reach out to the finance and other teams within the company, to ask them for information, or help"},
                {"role":"user","content": pr_prompt + "Conversation with format '[Person Name] said':\n" + conversation + "Clue:\n" + clue},
                {"role":"assistant","content":response},
                {"role":"user", "content": esc_prompt}, 
                ]
            )
    string = str(subject.choices[0].message.content)
    string = bylinestripper(string)
    start_idx = string.find("Subject:")+8
    end_idx = string.find("Description:")
    if start_idx != -1 and end_idx != -1:
        subj_string = string[start_idx:end_idx-1]
    else:
        subj_string = string
    subj_drops = ["Escalation for", "Escalation of", "escalation for", "escalation of",
                  "Urgent", "urgent", "URGENT", "Escalation", "escalation", "ESCALATION", 
                  "Escalate", "escalate", "ESCALATE", ": ", ":"]
    for droppedword in subj_drops:
        subj_string = subj_string.replace(droppedword,"")
    start_idx2 = string.find("Description:")+12
    if start_idx2 != -1:
        desc_string = string[start_idx2:]+"\n"
    else:
        desc_string = string + "\n"
    return subj_string, desc_string




#Define the individual pieces format that can be re-mixed in scenarios
elements = {
    "instlink": "_[Instructions](https://docs.google.com/document/d/1w6pg-Lqz1Y5n8Gah7JXTRAnNEgnLGDgQn0p4EE_DdyU/edit#bookmark=id.bazq9xp2u2jr)_\n",
    "action": "**What is your proposed action?** &nbsp;",
    "custop": "* Send to customer\n",
    "l2op": "* Send to L2\n",
    "extop": "* Send to external team\n",
    "clstop": "* Close ticket\n",
    "l1op": "* Send to L1\n",
    "buop": "* Elevate to BU\n",
    "clscop": "* Close chat\n",
    "divider_excl": "---",
    "divider": "---",
    "pr": "**PR**\n",
    #insert product name from prod dict
    "byline": "Best regards,\nNo_Name\n" +"X Support Team\n",
    "context": "**Additional context?** \n",
    "gpt": "**GPT**&nbsp;",
    "gptyes": "_Did you use GPT?_ Yes.\n",
    "gptno": "_Did you use GPT?_ No. Not required\n",
    #Adding sometimes used pieces 
    "blurbtask": "Set type to task and submit\n",
    "blurbbu": "Elevate to BU as this is within the BU scope as per the Routing Table.\n",
    "e2b": "\n".join([
        #add something so that text after Issue Summary: is not bolded in markdown
        "**Issue Summary:** &nbsp;",
        "**Reproduction Steps:** &nbsp;",
        "**Current Behaviour:** &nbsp;",
        "**Expected Behaviour:** &nbsp;",
        "**Troubleshooting Steps:** &nbsp;",
        "**Reason for Escalation (What do we want the BU to do?):** &nbsp;",
        "**Justification for Escalation(Why are we escalating?):** &nbsp;&nbsp;\n",]),
    "intuitIssue": "",
    "mhteam": "**External Team:** &nbsp; ",
    "mhreason": "**On Hold Reason:** &nbsp;",
    "mhtimer": "**On Hold Timer:** &nbsp; &nbsp; ",
    "mhtarget": "**Escalation Target:** &nbsp; &nbsp; ",
    #Options for mhteam
    "mhteam1": "BU Customer Success/Sales/SOP",
    "mhteam2": "Saas Ops",
    "mhteam3": "Internal",
    "mhteam4": "External to ESW",
    "mhteam5": "Engineering",
    "mhteam6": "Crossover HR",
    "mhteam7": "Crossover Finance",
    "mhteam8": "Central Finance",
    "mhteam9": "BU PS",
    "mhteam10": "BU Other",
    #add two empty lines after above line
    "ret": "\n",    
    #Add the SC options
    "sc1": "**SC**&nbsp;  **[emails](https://none)**",
    "sc2": "**Subject:**&nbsp;",
    "sc3": "**Description:**&nbsp;\n",
    "long_sc4": "**Attachments:**&nbsp; **[NA](https://none)**\n",
    #Pieces of Jira escalation
    #Insert Jira link from jira_links dict
    "jirabiz": "[Jira link]",
    "prepesc1": "**Issue Type:** &nbsp; ",
    "prepesc2": "**Subject:** &nbsp;\n",
    "prepesc3": "**Description:** &nbsp;\n",
    "prepesc4": "**Zendesk Ticket IDs:** &nbsp;",
    "long_prepesc5": "**Attachments:** &nbsp; **[NA](https://none)**\n",
    "prepesc6": "**Unit Type:** &nbsp;",
    "engesc1": "**Expected Behavior:** &nbsp; \n",
    "engesc2": "**Actual Behavior:** &nbsp; \n",
    "engesc3": "**Steps to Reproduce:** &nbsp; \n",
    "engescds": "**DS for Escalated Issue:** &nbsp; \n",
    "chg1": "**Link to Change Runbook:** &nbsp; \n",
    "chg2": "**Scheduled Start Time:** &nbsp; \n",
    "chg3": "**Scheduled End Time:** &nbsp; \n",
    "chg4": "**Change Requester:** &nbsp; \n",
    "chg5": "**Change Implementer:** &nbsp; \n",
    "intuitPR": "",
    "scrapedPR": "scraped_PR",
    "sumspace": " ",
    "alphaescinst": """

1. Review the escalation and if you agree. If not just Fail.
2. Don't fill anything in Escalation Fields and QC'er to check this before submitting.
3. Deliver the unit in Tempo.
3. Add an IN: “Escalation QC Pass” .
4. Set the ZD ticket to Pending. Wait a bit. Once it is in Pending - change Product to the proposed one in the escalation and submit as Open -> this triggers new AL with correct product (with all the credits and no extra ACs).
    """,
    "a_team"    : "Proposed Team: &nbsp; ",
    "a_desc"    : "Description: &nbsp; ",
    "a_req"     : "Requester: &nbsp; ",
    "a_student" : "Student Name: &nbsp; ",
    "a_app"     : "Learning App: ", 
    "a_date"    : "Date: &nbsp; ",
}

#Define a function to get input from a text file of the name
def get_name_from_file(dir_path):
    with open(dir_path+"/name.txt", "r") as f:
        agent_name = f.read()
        if agent_name != "John Doe\n":
            agent_name = agent_name.strip()
            agent_name = agent_name[:50]
            agent_name = agent_name + "\n"
        else:
            agent_name = "[AgentName]\n"
            wrapped = term_print_string("Please enter your name in the name.txt file in the program directory"," ")
            print_bright(wrapped,bredf)
        f.close()   
    return agent_name


#Define a function to get input from a text file to modify gpt model
#use_case = pr_model
#use_case = esc_model
#default_gpt_model = "gpt-4-1106-preview"
#default_gpt_model = "gpt-4"



#Define a rich text table for escalate to BU

def get_bu_esc_datatable(product,thedict):
    data = [
    [ "Issue Summary",thedict["intuitIssue"]],
    [ "Reproduction Steps", "NA"],
    [ "Current Behaviour", "NA"],
    [ "Expected Behaviour", "NA"],
    [ "Troubleshooting Steps","NA" ],
    [ "Reason for Escalation (What do we want the BU to do?)", "Please address the customer's issue."],
    [ "Justification for Escalation(Why are we escalating?)", f"{product} Routing Table"],
]
    html_table = "<table>"
    for row in data:
        html_table += "<tr>"
        for item in row:
            html_table += f"<td>{item}</td>"
        html_table += "</tr>"

    html_table += "</table>"
    e2b_value = html_table+"\n"
    return e2b_value


def dict_writer(orig_intent_list, global_intents_list, dict_to_update):
    intent_list = orig_intent_list.copy()
    conflict_elmnts = []
    staging_dict = {}
    def stage_it(element_name, element_value, override=False):
        nonlocal conflict_elmnts
        nonlocal staging_dict
        if element_name not in staging_dict:
            if element_value[:5] != dict_to_update[element_name][:5]:
                #print("firing first")
                staging_dict[element_name] = dict_to_update[element_name] + element_value
            else:
                #print("firing second")
                staging_dict[element_name] = element_value
        elif element_value != staging_dict[element_name] and not override:
            conflict_elmnts.append(element_value)
            conflict_elmnts.append(staging_dict[element_name])
            already_there = staging_dict[element_name].strip().replace("&nbsp;","").replace("https://none","<plchldr>")
            print(f"\n\nValue override:\n"
                  f"{already_there}\n"
                  f"-vs-\n {element_value}")
        else:
            #print("firing third")
            if element_value[:5] != dict_to_update[element_name][:5]:
                staging_dict[element_name] = dict_to_update[element_name] + element_value
            else:
                staging_dict[element_name] = element_valuetaging_dict[element_name] = element_value
        return
   

   #First takes precedence. It prints the above conflict statement but will keep the value of the first
    mapping_one_to_one = {
        "eng": [("mhteam","Engineering"),
                ("mhreason","Linked GHI"),
                ("mhtimer","9999 &nbsp;"),
                ("mhtarget","Engineering Defect &nbsp;"),
             ],
        "bz": [("mhteam","BU Customer Success/Sales/SOP"),
                ("jirabiz", "[Jira link]" + "(" + bu_jira_links["IGBIZOPS"] + ")\n"),
                ],
        "ibueng": [("mhteam","BU Other &nbsp;"),],
        "ztps": [("jirabiz", "[Jira link]" + "(" + bu_jira_links["ZTPS"] + ")\n"),
                 ],
        "cf_csquery": [("prepesc6","CSQuery\n")],
        "cf_wsf": [("prepesc6","WSF Payment\n")],
        "cf_udf": [("prepesc6","UDF\n")],
        "cf_writeoff": [("prepesc6","Write-off\n")],
        "cf_creditnote": [("prepesc6","Credit Note\n")],
        "cf_vendorreg": [("prepesc6","Vendor Registration\n")],
        "cf_vendorpay": [("prepesc6","Vendor Payment\n")],
        "cf_o2c": [("prepesc6","O2C\n")],
        "cf_tax": [("prepesc6","Tax Team Request\n")],
        "cf_treasury": [("prepesc6","Treasury Team Request\n")],
        "cf_generic": [("prepesc6","Collect Cash\n")],
        "bu_jira": [   ("mhteam","BU Other &nbsp;"),
                            ("mhreason","Linked JIRA"),
                            ("mhtimer","9999 &nbsp;"),
                            ("mhtarget","Other &nbsp;\n"),
                         ],
        "ext": [    ("mhteam","External to ESW"),
                    ("mhreason","Waiting to happen"),
                    ("mhtimer","168 &nbsp;"),
                    ("mhtarget","Other &nbsp;\n"),
                ],
        "bu": [ ("mhteam","BU Other &nbsp;"),
                ("mhreason","Awaiting elevation"),
                ("mhtimer","4 &nbsp;"),
                ("mhtarget","BU\n"),
               ],
        "categ_cf": [   ("mhteam","Central Finance &nbsp;"),
                        ("mhreason","CFIN-"),
                        ("mhtimer","9999 &nbsp;"),
                        ("mhtarget","Central Finance &nbsp;\n"),
                        ("prepesc1","Task\n"),
                        ("jirabiz", "[Jira link]" + "(" + bu_jira_links["CFIN"] + ")\n"),
                    ],
        "categ_saas": [ ("mhteam","Saas Ops &nbsp;"),
                        ("mhreason","Linked JIRA"),
                        ("mhtimer","9999 &nbsp;"),
                        ("mhtarget","Other &nbsp;\n"),
                        ("prepesc1","SaaS Incident\n"),
                       ],
        "categ_vp": [   ("mhteam","Internal &nbsp;"),
                        ("mhreason","SC to Product VP"),
                        ("mhtimer","9999 &nbsp;"),
                        ("mhtarget","Other &nbsp;\n"),
                     ],
        "categ_sc": [   ("mhteam","[**plc**](https://none)"),
                        ("mhreason","SC"),
                        ("mhtimer","168 &nbsp;"),
                        ("mhtarget","Other &nbsp;\n"),
                    ],
        "categ_accmgt": [   ("mhteam","BU Customer Success/Sales/SOP &nbsp;"),
                            ("mhtimer","168 &nbsp;"),
                            ("mhtarget","Other &nbsp;\n"),
                         ],

                       }
#for batch changed make a special category for the batch in mapping, and then make it fire here as an additional intent
    if any(intent in [item for item in global_intents_list if item.startswith("cf")] for intent in intent_list):
        intent_list.append("categ_cf")
   
    if any(intent == "saas" for intent in intent_list):
        intent_list.append("categ_saas")

    if any(intent == "chg_req" for intent in intent_list):
        stage_it("prepesc1","Change Request\n",True)
    
    if any(intent == "incident" for intent in intent_list):
        stage_it("prepesc1","SaaS Incident\n",True)

    if any(intent == "vp" for intent in intent_list):
        intent_list.append("categ_vp")
 
    if any(intent == "acc_mgt" for intent in intent_list):
        intent_list.append("categ_accmgt")
 
    if any(intent == "sc" for intent in intent_list):
        intent_list.append("categ_sc")
    
    if any(intent == "bz" for intent in intent_list): 
        intent_list.append("categ_bz")
    
    if any(intent == "bu_jira" for intent in intent_list):
        intent_list.append("categ_bujira")
        

    #main staging loop
    for intent in intent_list:
        if intent in mapping_one_to_one:
            changes = mapping_one_to_one[intent]
            for to_change, the_change in changes:
                stage_it(to_change,the_change)
    if "mhteam" in staging_dict:
        escalation_target = staging_dict.get("mhtarget", "error:intents didn't populate mhtarget").strip().lower()
        if "&nbsp; other" in escalation_target and any(intent not in ["exold","exoldn"] for intent in intent_list):
            staging_dict["mhtarget"] += "\n[Prep Escalation to be done by QC'er one step.](https://none)"

    #main dict update loop
    for key, value in staging_dict.items():
        dict_to_update[key] = value
    return

def remix_elements(orig_form,dict_of_elements):
    form = orig_form.copy()
    vallist = []
    for element_name in form:
        element_value = dict_of_elements[element_name]
        vallist.append(element_value)
    return "\n".join(vallist)


def link_updater(productname,intent_list,dict_of_elements):
    bu_jira_populated = False
    saas_jira_populated = False
    for key, value in bu_jira_links.items():
        if any(intent == key for intent in intent_list):
            matching_intent = next((intent for intent in intent_list if intent == key), None)
            dict_of_elements["jirabiz"] = "[Jira link]" + "(" + bu_jira_links[matching_intent] + ")"
            bu_jira_populated = True
            break
    if not bu_jira_populated:
        for key, value in saas_jira_links.items():
            if any(intent == key for intent in intent_list):
                matching_intent = next((intent for intent in intent_list if intent == key), None)
                dict_of_elements["jirabiz"] = "[Jira link]" + "(" + saas_jira_links[matching_intent] + ")"
                saas_jira_populated = True
                break
    
    if not saas_jira_populated and not bu_jira_populated:
        flag=None
        if "bu_jira" in intent_list:
            flag="bu"
        elif "saas" in intent_list:
            flag="saas"
        elif "cf" in intent_list:
            flag="cf"
        else:
            flag=None
            
        if productname in products_to_jiras:
            if flag in ["bu","cf"]:
                dict_of_elements["jirabiz"] = "[Jira link]" + "(" + products_to_jiras[productname][1] + ")"
            elif flag=="saas":
                dict_of_elements["jirabiz"] = "[Jira link]" + "(" + products_to_jiras[productname][0] + ")"
            else:
                dict_of_elements["jirabiz"] = "[Jira link]" + "(" + products_to_jiras[productname][0] + ") **Defaulting to SaaS Jira**"
        else: 
            dict_of_elements["jirabiz"] = "**[Jira not found](https://none)**"
    return dict_of_elements


def list_popper(orig_intent_list, orig_list_to_pop): # func modifies list
    intent_list = orig_intent_list.copy()
    list_to_pop = orig_list_to_pop.copy()

    if any(intent == "saas" for intent in intent_list):
        if "prepesc6" in list_to_pop:
            list_to_pop.remove("prepesc6")
        if "prepesc4" in list_to_pop:
            list_to_pop.remove("prepesc4")
    
    if any(intent == "chg_req" for intent in intent_list):
        try:
            lock = list_to_pop.index("prepesc3")+1
            add_list = ["chg1","chg2","chg3","chg4","chg5"]
            list_to_pop=list_to_pop[:lock] + add_list + list_to_pop[lock:]
        except ValueError:
            print("prepesc4 not found")

    return list_to_pop


def modify_string(string, scenario,prodname):
    string = string.replace("X Support Team", prodname + " Support Team")
    string = string.replace("<variable>", prodname)
    string = string.replace("\n* Elevate to BU", "* Elevate to BU")
    string = string.replace("\n* Send to L1", "* Send to L1")
    return string
   
   
#Building the printable forms by remixing_
sbpre = ["instlink","action"]
scntxt = ["divider", "context"]
spr = ["divider_excl", "pr", "intuitPR", "byline"]
sdvdr = ["divider"]
gpt = ["divider_excl", "gpt", "gptyes"]
meta = ["mhteam", "mhreason", "mhtimer", "mhtarget","ret"]
jira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4", "long_prepesc5", "prepesc6","ret"]
sc = ["sc1", "prepesc2","prepesc3","long_sc4"]
engesc = ["prepesc2", "prepesc3", "engesc1", "engesc2", "engesc3",]
alphaesc = ["a_team", "a_desc", "a_req", "a_student", "a_app", "a_date"]
forms = {
    "l1": sbpre + ["ret"] + ["l1op"] + scntxt + ["blurbtask"], #convert to task
    "cst": sbpre + ["custop"] + spr + gpt + scntxt+ ["ret"], #send to cust
    "exsc": sbpre + ["extop"] + spr + meta + sc + gpt + scntxt+ ["ret"], #prep esc via sc
    "exold": sbpre + ["extop"] + spr + meta + gpt + scntxt+ ["ret"], #customer update while in escalation
    "ex": sbpre + ["extop"] + spr + meta + scntxt + ["ret"], #escalate but no pr
    "exjira": sbpre + ["extop"] + spr + meta + jira + gpt + scntxt+ ["ret"], #prep esc to saas
    "exalpha": sbpre + ["alphaescinst"] + spr  + gpt + scntxt+ ["ret"], #prep esc to saas
    "exeng": sbpre + ["extop"] + spr + meta[:4]+["engescds"] + engesc + gpt + scntxt+ ["ret"], #prep esc to eng
    "exb": sbpre + ["extop"] + ["buop"] + spr + meta + ["e2b"] + gpt + scntxt + ["blurbbu"]+ ["ret"], #elevate to bu
    "l2": sbpre + ["l2op"] + spr + gpt + scntxt+ ["ret"], #send to l2
    "clst": sbpre + ["clstop"] + spr + gpt + scntxt + ["ret"], #close ticket
    "clsch": ["sumspace"] +sbpre + ["clscop","ret"], #close chat
    "sum": ["intuitPR","byline"],
    }

temp_dict = {}
for key, sequence in forms.items():
    nkey = key+"n"
    stage_a_list = spr + gpt + jira + sc + engesc
    exclusion_list = [item for item in stage_a_list if item not in ["ret"]] 
    nvalue = list(filter(lambda x: x not in exclusion_list, sequence))
    temp_dict[nkey] = nvalue
forms.update(temp_dict)


half_list = ["l1", "cst", "exsc", "exold", "ex", "exalpha", "exjira", "exeng", "exb", "l2", "clst", "clsch", "sum"] 
full_list = half_list + [item+"n" for item in half_list]

scenarios_requiring_pr = list(filter(lambda x: x not in ["clsch"], half_list))
scenarios_requiring_esc = [item for item in full_list if item.startswith("e") and not item.endswith("n") and not item in ["exb","exold"]]


def main():
    #Global scope vars for printing
    terminal_width = shutil.get_terminal_size().columns
    chrt = "|" #· ⋮
    subindent = " "+chrt+" "
    available_width = terminal_width - len(subindent)

    #Get the main dict in pure form
    elements_orig = {
        "instlink": "_[Instructions](https://docs.google.com/document/d/1w6pg-Lqz1Y5n8Gah7JXTRAnNEgnLGDgQn0p4EE_DdyU/edit#bookmark=id.bazq9xp2u2jr)_\n",
        "action": "**What is your proposed action?** &nbsp;",
        "custop": "* Send to customer\n",
        "l2op": "* Send to L2\n",
        "extop": "* Send to external team\n",
        "clstop": "* Close ticket\n",
        "l1op": "* Send to L1\n",
        "buop": "* Elevate to BU\n",
        "clscop": "* Close chat\n",
        "divider_excl": "---",
        "divider": "---",
        "pr": "**PR**\n",
        #insert product name from prod dict
        "byline": "Best regards,\nNo_Name\n" +"X Support Team\n",
        "context": "**Additional context?** \n",
        "gpt": "**GPT**&nbsp;",
        "gptyes": "_Did you use GPT?_ Yes.\n",
        "gptno": "_Did you use GPT?_ No. Not required\n",
        #Adding sometimes used pieces 
        "blurbtask": "Set type to task and submit\n",
        "blurbbu": "Elevate to BU as this is within the BU scope as per the Routing Table.\n",
        "e2b": "\n".join([
            #add something so that text after Issue Summary: is not bolded in markdown
            "**Issue Summary:** &nbsp;",
            "**Reproduction Steps:** &nbsp;",
            "**Current Behaviour:** &nbsp;",
            "**Expected Behaviour:** &nbsp;",
            "**Troubleshooting Steps:** &nbsp;",
            "**Reason for Escalation (What do we want the BU to do?):** &nbsp;",
            "**Justification for Escalation(Why are we escalating?):** &nbsp;&nbsp;\n",]),
        "intuitIssue": "",
        "mhteam": "**External Team:** &nbsp; ",
        "mhreason": "**On Hold Reason:** &nbsp;",
        "mhtimer": "**On Hold Timer:** &nbsp; &nbsp; ",
        "mhtarget": "**Escalation Target:** &nbsp; &nbsp; ",
        #Options for mhteam
        "mhteam1": "BU Customer Success/Sales/SOP",
        "mhteam2": "Saas Ops",
        "mhteam3": "Internal",
        "mhteam4": "External to ESW",
        "mhteam5": "Engineering",
        "mhteam6": "Crossover HR",
        "mhteam7": "Crossover Finance",
        "mhteam8": "Central Finance",
        "mhteam9": "BU PS",
        "mhteam10": "BU Other",
        #add two empty lines after above line
        "ret": "\n",    
        #Add the SC options
        "sc1": "**SC**&nbsp;  **[emails](https://none)**",
        "sc2": "**Subject:**&nbsp;",
        "sc3": "**Description:**&nbsp;\n",
        "long_sc4": "**Attachments:**&nbsp; **[NA](https://none)**\n",
        #Pieces of Jira escalation
        #Insert Jira link from jira_links dict
        "jirabiz": "[Jira link]",
        "prepesc1": "**Issue Type:** &nbsp; ",
        "prepesc2": "**Subject:** &nbsp;\n",
        "prepesc3": "**Description:** &nbsp;\n",
        "prepesc4": "**Zendesk Ticket IDs:** &nbsp;",
        "long_prepesc5": "**Attachments:** &nbsp; **[NA](https://none)**\n",
        "prepesc6": "**Unit Type:** &nbsp;",
        "engesc1": "**Expected Behavior:** &nbsp; \n",
        "engesc2": "**Actual Behavior:** &nbsp; \n",
        "engesc3": "**Steps to Reproduce:** &nbsp; \n",
        "engescds": "**DS for Escalated Issue:** &nbsp; \n",
        "chg1": "**Link to Change Runbook:** &nbsp; \n",
        "chg2": "**Scheduled Start Time:** &nbsp; \n",
        "chg3": "**Scheduled End Time:** &nbsp; \n",
        "chg4": "**Change Requester:** &nbsp; \n",
        "chg5": "**Change Implementer:** &nbsp; \n",
        "intuitPR": "",
        "scrapedPR": "scraped_PR",
        "sumspace": " ",
        "alphaescinst": """

1. Review the escalation and if you agree. If not just Fail.
2. Don't fill anything in Escalation Fields and QC'er to check this before submitting.
3. Deliver the unit in Tempo.
3. Add an IN: “Escalation QC Pass” .
4. Set the ZD ticket to Pending. Wait a bit. Once it is in Pending - change Product to the proposed one in the escalation and submit as Open -> this triggers new AL with correct product (with all the credits and no extra ACs).
    """,
    "a_team"    : "Proposed Team: &nbsp; ",
    "a_desc"    : "Description: &nbsp; ",
    "a_req"     : "Requester: &nbsp; ",
    "a_student" : "Student Name: &nbsp; ",
    "a_app"     : "Learning App: ", 
    "a_date"    : "Date: &nbsp; ",

    }
    #repopulate elements from _orig
    global elements
    for key in elements:
        elements[key] = elements_orig[key]

    sys_prompt = prompts['sys']
    pr_prompt = prompts['pr']
    sum_prompt = prompts['sumx'] 
    esc_prompt = prompts['esc']

    #Print the logo
    sep = " "+"-"*(terminal_width-2)
    print(sep)
    print_logo()
    print("-"*(terminal_width-2))


    #BELOW THE CUT
    html_content = None
    soup = None
    target_div = None
    ticket_soup = None

    html_content = pyperclip.paste()
    if html_content == None:
        html_content = "Nothing"

    if html_content.startswith("<html"):
        soup = BeautifulSoup(html_content, 'html.parser')
        #TAPE - PFFU - Potential for Fuck Ups
        target_div = soup.find("div", {"class": "ticket-panes-grid-layout active sc-9rzm4f-0 cusuqB"}) 
        ticket_soup = soup.find("div", {"class": "sc-lzuyri-0 gOXeKF"})
        if target_div:
            soup = target_div
        #END TAPE
        f_pr = get_first_pr(soup)
        conversation,list_of_messages,names = get_zd_messages(soup,f_pr)
        amended_list = append_identities(list_of_messages,names)
        resp_list = get_intuitSummary(amended_list) 
        print_bright("__Issue:",greenf)
        print_bright(term_print_string(resp_list[0]," "),whitef)
        print_bright("__Actions taken:", greenf)
        print_bright(term_print_string(resp_list[1]," "),whitef)
        print_bright("__Now:",greenf)
        print_bright(term_print_string(resp_list[2], " "),whitef)

    else:
        print_bright("No HTML content found in clipboard. Please copy a Zendesk ticket or chat conversation and try again.",bredf)
        soup = BeautifulSoup("<html></html>", 'html.parser')
        f_pr = ""
        conversation = ""
    
    elements["byline"] =  "Best regards,\n"+ agent_name+"\nX Support Team\n"
    main_scenario_instruction = (   "Pick a scenario:\ne.g. type '1', or type 'alt 1' for DS only no pr.\n\n"
                                    "1  - Send to customer\n"
                                    "2  - Close ticket - with a PR\n"
                                    "3  - Place back on hold - with a PR\n"
                                    "4  - Send to external team (via an SC)\n"
                                    "5  - Send to external team (SaaS Inc.)\n"
                                    "6  - Send to external team (SaaS Chg Req)\n"
                                    "7  - Send to external team (Engineering)\n"
                                    "8  - Send to external team (BU Jira)\n"    
                                    "9  - Send to external team (CFIN)\n"
                                    "10 - Send to L1 - no PR\n"
                                    "11 - Send to L2 - with a PR\n"
                                    "12 - Elevate to BU - with a PR\n"
                                    "13 - Summarize chat\n"
                                    "14 - Close chat - no PR\n\n"
                                    "Press Enter to reload."
                                 )
    wrapped_instruction = term_print_string(main_scenario_instruction, " ")
    print("\n")
    print_bright(wrapped_instruction,greenf)
    print(sep)
    
    #INPUT
    chosen_scenario = "" 
    intentions_list = [] 
    information = "" 
    processed_quit_terms = [term.strip().replace(" ~","") for term in intent_sets["quit"]]
    while not chosen_scenario:
        user_input = input(" ")
        if user_input == "":
            user_input = " re ~"
        chosen_scenario, intentions_list  = scenario_extractor(user_input) #TAPE - part of the effort to make it 2step removed clue/information from output of this func:
         
    if chosen_scenario in ["restart"]: 
        print_bright(" Restarting...",magf)
        time.sleep(0.3) #debug
        clear_terminal()
        return 
    
    if chosen_scenario in ["quit"]:
        print_bright(" Goodbye!",magf)
        sys.exit()

    elif chosen_scenario in forms:
        if chosen_scenario[-1] != "n" and chosen_scenario != "sum":
            print("\n")
            clue_text = term_print_string("What should Wingman tell the customer? | Clue:\n", " ")
            print_bright(clue_text,greenf)
            information = input(" ")
            list_of_saas_replace = [" Infra ", " infra ", " Saas ", " SaaS ", " saas "]
            for item in list_of_saas_replace:
                information = information.replace(item, " Infrastructure ")
        else:
            information= ""
        
        if information in ["restart", "refresh", "redo","re"]:
            print_bright(" Restarting...",magf)
            time.sleep(0.3) #debug
            clear_terminal()
            return
         
        elif information in processed_quit_terms:
            print_bright(" Goodbye!",magf)
            sys.exit()
        
        processing_info_string = term_print_string("Processing...", " ")
        print_bright(processing_info_string, magf)
        ticket_prodname = ""
        ticket_prodname = get_product(soup)
        ticket_number = "" 
        ticket_number = get_ticket_number(ticket_soup)
        response = ""

        if chosen_scenario in scenarios_requiring_pr: #debug
            if chosen_scenario in ["sum"]:
                prompt_to_use = sum_prompt
                information = "N/A"
            else:
                prompt_to_use = pr_prompt
            #Insert product in prompt 
            prompt_to_use = prompt_to_use.replace("<product>", ticket_prodname,1)
            response = get_intuitPR(pr_model,conversation,information,sys_prompt,prompt_to_use)
            elements["intuitPR"] = response

        subjstring = "" 
        desc_string = "" 
        issuestring = ""

        if chosen_scenario in ["exb",] and not any(intent == "no_esc" for intent in intentions_list):
            issuestring = get_intuitIssue(esc_model,conversation,response,sys_prompt)
            elements["intuitIssue"] = issuestring 
        
        if chosen_scenario in ["exb","exbn"]:
            elements["e2b"] = get_bu_esc_datatable(ticket_prodname,elements)  # func using dict 
        
        if chosen_scenario in scenarios_requiring_esc and not any(intent == "no_esc" for intent in intentions_list):
            subjstring, desc_string = get_intuitEsc(esc_model,conversation,response,elements,information,sys_prompt,pr_prompt,esc_prompt) # func using dict
            elements["prepesc2"] = "**Subject:** &nbsp;" + subjstring
            if chosen_scenario in ["exsc","exscn"]:
                elements["prepesc3"] = "**Description:** &nbsp;\n\n" + "Dear **[Person](https://none)**,\n\n Context: &nbsp;ZD&nbsp;#" + ticket_number + "\n" + desc_string + "\n"
            else:
                elements["prepesc3"] += desc_string 

        #Write non AI stuff to dict
        elements = link_updater(ticket_prodname,intentions_list,elements) #func using dict
        elements["prepesc4"] += ticket_number+"\n"
        dict_writer(intentions_list, global_intents_list,elements) # func using dict
      
        used_form = copy.deepcopy(forms[chosen_scenario])
        used_form = list_popper(intentions_list, used_form)

        #Stringing
        finalstring = ""
        finalstring = remix_elements(used_form,elements) # func using dict
        finalstring = modify_string(finalstring,chosen_scenario,ticket_prodname)
       
        #Term output
        ds_printer(finalstring)
         
        #Copy to clipboard
        pyperclip.copy(finalstring)
        

    else:
        print("Scenario is not defined")

    last_input = ""
    last_term_print = term_print_string("Click bookmarklet - and press Enter...", " ")
    print_bright(last_term_print,greenf)
    last_input = input(" ")
    last_input = last_input+" ~"
    if last_input in intent_sets["quit"]:
        print_bright(" Goodbye!",magf)
        sys.exit()
    else: 
        print_bright(" Restarting...",magf)
        time.sleep(0.3) #debug
        clear_terminal()
        return
    
    
while True:
    main()


