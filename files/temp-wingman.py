##A scripting tool
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


#javascript:(function() { var htmlContent = document.documentElement.outerHTML; navigator.clipboard.writeText(htmlContent); })();

# ANSI escape codes for bright colors
bluef = "\033[94;1m"
lbluef = "\033[96m"
yellowf = "\033[93;1m"
greenf = "\033[92m"
magf = "\033[95m" 
bcyanf= "\033[96m"
bgreenf = "\033[32m"
lgreyf = "\033[37m"
whitef = "\033[97;1m"
bredf = "\033[91m"
resetf = "\033[0m" 

#Find the path where the script is running 
# to default to config bundled with the executable
def get_resource_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        print("Error: Could not find the resource path in sys._MEIPASS.")
        base_path = os.path.abspath(".")
    return base_path

#Get the files from the users documents directory
home_path = os.path.expanduser("~")
set_dir_path = os.path.join(home_path, "Documents", "wingman","appdata")
fallback_path = os.path.join(get_resource_path(),"appdata")

dir_path = None
if not dir_path:
#python script defined path - non executable
    try:
        file_path = os.path.abspath(__file__)
        wingman_dir_path = os.path.dirname(file_path)
        dir_path = os.path.join(wingman_dir_path,"appdata")
        print("dir_path intuited from python script dir")
#windows executable - defined path in runbook to place config
    except Exception:
        try:
            dir_path = set_dir_path
            print("dir_path is set to ~/Documents/wingman/appdata")
#fallback to bundled appdata
        except Exception:
            try:
                dir_path = fallback_path
            except Exception:
                print("Error: Could not find the resource path in sys._MEIPASS.")
                dir_path = os.path.abspath(".")

config = configparser.ConfigParser()
try:
    config.read(os.path.join(dir_path, 'config.ini'))
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
    esc_model = get_gpt_from_file("esc_model",dir_path,"gpt-4-1106-preview")

#get the gpt model for prs
try:
    pr_model_value = config['Models']['pr_model']  
    if "gpt-4-turbo" in pr_model_value:
        pr_model = "gpt-4-1106-preview"
    elif "gpt-4" in pr_model_value:
        pr_model = "gpt-4"
except KeyError:
    pr_model = get_gpt_from_file("pr_model",dir_path,"gpt-4-1106-preview")


#Fileload products and their jira links from json files

try:
    with open(os.path.join(dir_path, 'products_to_jiras.json'),'r') as f:
        products_to_jiras = json.load(f)
except json.JSONDecodeError:
    print("The products_to_jiras.json file is corrupted or invalid.")
except FileNotFoundError:
    print("The products_to_jiras.json file is missing.")
except Exception as e:
    print("An error occured while loading the products_to_jiras.json file.")
    print(e)

try:
    with open(os.path.join(dir_path, 'saas_jira_links.json'),'r') as f:
        saas_jira_links = json.load(f)
except json.JSONDecodeError:
    print("The saas_jira_links.json file is corrupted or invalid.")
except FileNotFoundError:
    print("The saas_jira_links.json file is missing.")
except Exception as e:
    print("An error occured while loading the jira_links.json file.")
    print(e)


try:
    with open(os.path.join(dir_path, 'bu_jira_links.json'),'r') as f:
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

os.environ["OPENAI_API_KEY"]= api_key


#Global scope vars for printing
terminal_width = shutil.get_terminal_size().columns
chrt = "|" #· ⋮
subindent = " "+chrt+" "
available_width = terminal_width - len(subindent)

#Global scope vars for ZD scraping
class_kandy2 = 'sc-5rafq2-0 gEMoXX'
class_chat = 'sc-wv3hte-1 epkhmy'
class_chat2 = 'sc-wv3hte-0 eKImJ'
class_AI_integration = "sc-5rafq2-0 sc-7uf44v-0 gXPtvy"
pr_classes = [class_kandy2,class_chat,class_chat2,class_AI_integration, "sc-11lm90w-0 dehgfD","sc-54nfmn-2 bLEhML"]


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
        "restart" : [" refresh ~"," restart ~", " redo ~", " re ~" ], #if entire value is this is implied by starting space and the ending char ~
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
        "sc" : [ " sc ","side conv", "side conversation", " ex ",],
        "bz" : [" bz ", "business ops", "bizops ", "exbz",],
        "bu_jira" : [ " bu jira ", "ibueng", "ignite bu eng", "itpef", "ztps", "business ops", " bz ", "bizops", "exbz",],
        "jira_generic" : ["on jira", " jira ", " jra ", " jir ", " jirn ", " jiran",],
        "acc_mgt" : [" acc ", "account management", "account manager", " am ", " accm ", " accmg ", " accman ", " accmn ", " accmgt "],
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

intent_sets["force_elevate"] = [x+" "+ y.strip() for x in negations for y in intent_sets["force_esc"]]

intent_sets["force_elevate"] += ["send to bu", "elevation to", "elevate to bu", "elevate to the bu", "bu elevation", "via elev", 
                           "to the bu", "send to the bu", "through elev", "by elev", "on elev", "over elev", 
                           "not on jira", "not through jira", "not via jira", "not on sc", 
                           "not through sc", "not via esc", "not through esc", "not on esc",
                           "not via side", "not through side", "not on side", "not via elev",
                            "not through elev", "not on elev", "not over elev", "not by elev",
                            "not by sending an sc", "not by sending a sc", "not by sending a side",]

intent_sets["force_esc"] += [x+" "+ y.strip() for x in negations for y in intent_sets["force_elevate"]]

insertion = {        
        "chat": ["clsch"," chat ", " cht ",],
        "clst" : ["ticket", " tkt ", " tckt ","clst"],
        "saas" : [" saas ", " infra t", " infrastructure t", " exsaas "],
        "incident" : [" inc","incident", "incdt"],
        "chg_req" : ["change request", "chng req", "chg req", "chngreq"],
        "in_esc_update" : [item for item in intent_sets["no_esc"]] + ["in escalation", "in esc ", "pending input",
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
            "vp"            :["exsc","exscn"],
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
            "sc"            :["exsc", "exscn","exold","exoldn"],
            "bz"            :["exjira", "exjiran","exold","exoldn"],
            "bu_jira"       :["exjira", "exjiran","exold","exoldn"],
            "jira_generic"  :["exjira", "exjiran","exold","exoldn"],
            "acc_mgt"       :["exsc", "exscn","exjira", "exjiran","exold","exoldn"],
            "eng"           :["exeng", "exengn","exold","exoldn"],
            "bu"            :["exb","exbn",],
            "force_esc"     :[item for item in full_list if item not in ["exb", "exbn"]],
            "force_elevate" :[item for item in full_list if item not in ["exsc", "exscn","exjira","exjiran"]],
            "chat"          :["clsch"],
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
def print_bright(message, color_code):
    print(f"{color_code}{message}{resetf}")

def term_print_string(string,indent):
        wrapped_out = []
        string = string.replace("\n","}n")
        stringlist = string.split("}n")
        for sliver in stringlist:
            wrapped_sliver = textwrap.fill(sliver, width = terminal_width-len(indent), 
                                           initial_indent = indent, 
                                           subsequent_indent = indent)
            wrapped_sliver = wrapped_sliver.replace("}n","\n")
            wrapped_out.append(wrapped_sliver)
        string_out = "\n".join(wrapped_out)
        return string_out

def print_wrapped(string,color):
     wrapped_string = textwrap.fill(string, width = terminal_width-4, initial_indent = "    ", subsequent_indent = "    ")
     print_bright(wrapped_string,color)

def print_logo():
    logo1 = "\\\\    /X    //\n \\\\  //\\\\  //\n  \\\\//  \\\\// \n   V/    V/  "

    logo2 ="""
.Wxx       w        Wx    
  yxw     cWWw     1Wx  
    Ww. cW   Ww   xW   
     Ww.W     W@|wW   
      WW       @xW   
                       """
    lines = logo1.split("\n")
    count = 0
    for line in lines:
        #line = line[:19]
        #charlist = []
        #for char in line:
         #   char = char.replace(char,2*char)
          #  charlist.append(char)
        #line = "".join(charlist)
        filler="."
        compute = round((55-len(line)-20)/2)
        line = line.replace(" ",filler)
        decoration = filler*(compute-count*2)
        line = decoration + line + decoration 
        print_bright(line.center(terminal_width-2),whitef)
        count += 1

    print_bright(textwrap.fill("Wingman v0.7beta",
                               terminal_width-10)
                                .rjust(terminal_width-4),whitef)
def clear_terminal():
    if platform.system() == "Windows":
        os.system('cls')  
    else:
        os.system("clear && printf '\033[3J'")  

def set_terminal_size(rows, columns):
    if platform.system() == "Windows":
        os.system(f'mode con: cols={columns} lines={rows}')

set_terminal_size(30, 100)

def preserve_newlines(tag):
    text_parts = []
    for element in tag.descendants:
        if element.parent.name == "a":
            continue
        if isinstance(element, NavigableString):
            text = str(element).replace("\n", "[newline]")
            text_parts.append(text)
        elif element.name == "br":
            text_parts.append("[newline]")
        elif element.name == "p":
            text_parts.append("[newline]")
        elif element.name == "li":
            second_last = len(text_parts) -1
            text_parts.insert(second_last, "* ",)
            text_parts.append("[newline]")
        elif element.name == "strong":
            text_parts.insert(len(text_parts), "__",)
        elif element.name == "/strong":
            text_parts.append("__")

        #elif element.name == "a":
         #   text_parts.append(str(element))
    return ''.join(text_parts).replace("[newline]", "\n")

def firstpr_extractor(soup):
    comment_text = ""
    class_list_firstpr = ['sc-54nfmn-1 bthKwz','sc-1qvpxi4-1 lvXye','sc-i0djx2-0 fwLKxM']
    class_list_firstpr.extend(pr_classes)
    for div in soup.find_all('div', {'class': class_list_firstpr}):
        if div is None:
            print("No div")
        else:
            comment_div = div.find('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2]})
            if comment_div:
                comment_text_pre = comment_div.text[:2000]
                comment_text = bylinestripper(comment_text_pre)
            break
    return comment_text

#ticket_soup sc-lzuyri-0 gOXeKF
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


def bylinestripper(string):
    start_idx = string.find("Warm regards,")
    if start_idx == -1:
        start_idx = string.find("Best regards")
    if start_idx == -1:
        start_idx = string.find("Best Regards")
    if start_idx == -1:
        start_idx = string.find("Regards")
    if start_idx == -1:
        start_idx = string.find("Sincerely,")
    if start_idx == -1:
        start_idx = string.find("Kind regards,")
    if start_idx == -1:
        start_idx = string.find("Thanks,")
    if start_idx == -1:
        start_idx = string.find("Best regard,")
    if start_idx == -1:
        start_idx = string.find("Best,")
    if start_idx != -1:
        return string[:start_idx-1] #Also removes message history after byline
    else:
        return string

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

def get_zd_messages(soup,f_pr):  
    zd_messages = []
    messagecounter = []

    
#Add a feature to scrape the first message if it is an IN
    first_IN = ""
    first_IN_pre = ""
    first_commentorIN = ""
    sender_name = "John Doe"
    subj = ""
    for text in soup.find_all('input', {'class': 'sc-1nvv38f-6 icxrHc StyledTextInput-sc-k12n8x-0 bXXlCE'}):
        subj = text['value']
        break
    if subj != "":
        subj = " Subject: " +  subj
    else:
        subj = ""
    print_bright(subj,yellowf)

    for div in soup.find_all('div', {'class':['sc-1wvqs23-0 dTcJJt','sc-qzyw2x-0 kTuPsA']}):
        if div is None:
            print("No div when looking for first IN ATTENTION")
        else:
            all_comments = div.find_all_next('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled']})
            if all_comments:
                for comment in all_comments:   
                    first_commentorIN =  comment.text #MAIN EXTRACTION
                    first_IN_pre = bylinestripper(first_commentorIN)
                    break
            strong_text = div.find('strong')
            sender_name = "No name"
            if strong_text:
                sender_name = strong_text.text.strip()
                if sender_name.find(" "):
                    sender_name = sender_name.split()[0]

            numtal_IN = 0 
            for char in sender_name:
                assignednum_IN = ord(char)
                numtal_IN = numtal_IN + assignednum_IN
            if numtal_IN not in messagecounter:
                messagecounter.append(numtal_IN)

            first_IN = sender_name+ " said: \n " + "| " + first_IN_pre
#            print("\nfirst_IN: \n" + first_commentorIN[:50])
#            print("\nfirst_pr: \n' " + f_pr[:50])
            break

    if first_commentorIN[:50] != f_pr[:50]:
        #print("\n Making SURE to print first IN as it is different from the inclusion in messages \n")
        print_bright(" "+sender_name + ": ",whitef)
        #print("first IN fired:" + repr(sender_name)) #debug
        fed_IN = first_IN_pre.replace("\n\n","}n")
        fed_IN = fed_IN.replace("\n","}n")
        split_IN = fed_IN.split("}n")
        split_IN_print_list = []
        for sliver in split_IN:
            wrapped_comment = textwrap.fill(sliver,
                                            width=available_width,                                        
                                            initial_indent=subindent,
                                            subsequent_indent=subindent,
                                            )
            split_IN_print_list.append(wrapped_comment) 
        wrapped_comment = "\n".join(split_IN_print_list)  
        wrapped_comment = wrapped_comment.replace("}n","\n "+chrt + " ")
        print_bright(wrapped_comment+"\n",yellowf) #main printing is happening here
    zd_pr_list = ['sc-54nfmn-1 bthKwz','sc-1qvpxi4-1 lvXye','sc-i0djx2-0 fwLKxM']
    zd_pr_list.extend(pr_classes)
    for div in soup.find_all(['div','bdi'], {'class': zd_pr_list}):

        if div is None:
            print("No div") 
        else:
            sender_name = "No name"
            for title in div.find_all_previous('div', {'class': ['sc-1gwyeaa-2 icjiLH','sc-yhpsva-1 dtIjfP']}):
                strong_text = title.find('strong')
                if strong_text:
                    sender_name_pre = strong_text.text.strip()
                    if sender_name_pre.find(" "):
                        sender_name = sender_name_pre.split()[0]
                    break
            numtal = 0
            for char in sender_name:
                assignednum = ord(char)
                numtal = numtal + assignednum
            if numtal not in messagecounter:
                messagecounter.append(numtal)
            if numtal in messagecounter:
                index = messagecounter.index(numtal)+1

        # Get the Comment      
            comment_div = div.find(['div','bdi'], {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2, "sc-11lm90w-0 dehgfD"]})
            comment_text = "No comment"
            if comment_div is not None:
                comment_text_pre = preserve_newlines(comment_div)
                comment_text_pre = comment_text_pre[:2000]
                comment_text = bylinestripper(comment_text_pre)
                comment_text_temp_strip = comment_text.replace("\n"," ")
                comment_text_temp_strip = comment_text_temp_strip.replace("\xa0"," ")
                comment_text_temp_strip = ' '.join(comment_text_temp_strip.split())                
                chars_rm = len(comment_text) - len(comment_text_temp_strip)
                idx_name = comment_text_temp_strip.find(sender_name_pre)
                if idx_name != -1:
                    idx_name_slicer = comment_text.rfind(sender_name) 
                    comment_text = comment_text[:idx_name_slicer]
                else:
                    idx_name = comment_text.find("I declare that the data in this ticket")
                    if idx_name != -1:
                        comment_text = comment_text[:idx_name]
            if comment_text != "No comment":
                print_bright(" "+sender_name + ": ",whitef)
                #print("Main fired:" + repr(sender_name)) #debug
                fed_comment = comment_text.replace("\n\n\n","}n}n")
                fed_comment = comment_text.replace("\n\n","}n}n")
                fed_comment = fed_comment.replace("\n","}n")
                split_fed = fed_comment.split("}n")
                split_fed_print_list = []
                for sliver in split_fed:
                    wrapped_comment = textwrap.fill(sliver, 
                                                    width=available_width,
                                                    initial_indent=subindent,
                                                    subsequent_indent=subindent,
                                                    )
                    split_fed_print_list.append(wrapped_comment) 
                if split_fed_print_list:
                    if split_fed_print_list[0] == "":
                        split_fed_print_list.pop(0)
                    if split_fed_print_list[-1] == "":
                        split_fed_print_list.pop(-1)
                wrapped_comment = "\n".join(split_fed_print_list)
                wrapped_comment = wrapped_comment.replace("\n\n\n","\n "+chrt+" \n")
                wrapped_comment = wrapped_comment.replace("\n\n","\n "+chrt+" \n")
                wrapped_comment = wrapped_comment.replace("}n","\n "+chrt+" ")
                #if the counter is an even number
                if index == 1:    #main printing is happening here 
                    print_bright(wrapped_comment,yellowf)
                    underliner = "`"*(terminal_width-4)
                    print("\n")
                    #print_bright(underliner.center(terminal_width),yellowf)
    #                elif index == 1:
    #                    print_bright(wrapped_comment+"\n",yellowf)
    #                elif index == 3:
    #                    print_bright(wrapped_comment+"\n",magf)
    #                elif index == 4:
    #                    print_bright(wrapped_comment+"\n",greenf)
    #                elif index % 2 != 0:
    #                    print_bright(wrapped_comment+"\n",bredf)
                else:
                    print_bright(wrapped_comment,bcyanf) #main printing is happening here
                    print("\n")
                    #print_bright(underliner.center(terminal_width),bcyanf)
                zd_messages.append(f"{sender_name} said: \n | {comment_text}")

    zd_messages_str = "\n".join(zd_messages)
    if first_commentorIN[:50] == f_pr[:50] and len(zd_messages_str) > 100:
        zd_messages_str =  zd_messages_str[-7000:]
    else:
        zd_messages_str =  first_IN + "\n" + zd_messages_str[-7000:]
    found_colon = zd_messages_str.find(":")
    if found_colon != -1:
        zd_messages_str = zd_messages_str[:found_colon+1] + "\n" + subj + "\n" + zd_messages_str[found_colon+1:]
#    with open(f"{dir_path}/logs/log_last_zd_messages.txt", "w") as f:
#        f.write("ZD MESSAGES including FIRST IN: \n\n" + zd_messages_str)
#    with open(f"{dir_path}/logs/log_last_zd_messages.txt", "a") as f:
#        f.write("\n\n\n\n\n\nfirst_IN FOUND: \n" + first_IN)
    return zd_messages_str



def get_intuitPR(model_input,conversation,preseeded_context,seededclue,pr_promptsys,pr_prompt1,pr_prompt2):
    client = OpenAI()
    if preseeded_context != "":
        clue = preseeded_context
    else:
        clue = seededclue
#gpt-4-1106-preview
    #print("Processing clue: " + clue[:40])
    #print("Processing conversation: " + conversation[:40])
    #print("Processing preseeded_context: " + preseeded_context[:40])
    #print("Processing pr_prompt1: " + pr_prompt1[:40])
    #print("Processing pr_promptsys: " + pr_promptsys[:40])
    completion = client.chat.completions.create(
        model=model_input,
      
        messages=[
        {"role": "system", "content": pr_promptsys},
        {"role": "user", "content": pr_prompt1 + "Conversation:\n" + conversation + "Clue:\n" + clue},
        #{"role": "assistant", "content": "<response redacted>"},
        #{"role": "user", "content": pr_prompt2},
        ]
    )
    
    string = str(completion.choices[0].message.content)
    string = bylinestripper(string) 
    return string

def get_intuitIssue(model_input,conversation,response,pr_promptsys):
    client = OpenAI()
    subject = client.chat.completions.create(
            model=model_input,
            messages=[
                {"role":"system","content": "You are a customer support agent routing customer issues to other teams"},
                {"role":"user","content":  "Look at the messages in conversation and the last response sent to the customer, then summarize the customer issue in a single line or very short para, retain specific information:\n" + conversation + "Response:" + response},
                ]
            )
    string = str(subject.choices[0].message.content)
    return string


#Its not nice that dict is getting written to directly for the prepesc2 key. TAPE
def get_intuitEsc(model_input,conversation,response,dictname,clue,pr_promptsys,pr_prompt1,pr_prompt2,pr_prompt3):
    client = OpenAI()
    subject = client.chat.completions.create(
            model=model_input,
            messages=[
                {"role":"system","content": pr_promptsys +"Sometimes have to reach out to the finance and other teams within the company, to ask them for information, or help"},
                {"role":"user","content": pr_prompt1 + "Conversation with format '[Person Name] said':\n" + conversation + "Clue:\n" + clue},
                {"role":"assistant","content":response},
                {"role":"user", "content": pr_prompt3}, 
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

def get_gpt_from_file(use_case,dir_path,default_gpt_model):
    with open(dir_path+"/config.ini", "r") as f:
        config_text = f.read()
        where_use_case = config_text.find(use_case+" = ") 
        if where_use_case != -1:
            post_where_use_case = where_use_case + len(use_case+" = ")
            use_case_model_value = config_text[post_where_use_case:post_where_use_case+12]
            use_case_model_value = use_case_model_value.strip()
            if "gpt-4-turbo" in use_case_model_value:
                use_case_model = "gpt-4-1106-preview"
            elif "gpt-4" in use_case_model_value:  
                use_case_model = "gpt-4"
            else:
                use_case_model = default_gpt_model
                print(f"{use_case} model 'value' incorrect in wm_config.txt. Using {default_gpt_model}")
        else:
            use_case_model = "gpt-4-1106-preview"
            print(f"{use_case} model not found in wm_config.txt. Using {default_gpt_model}")
        return use_case_model        


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
        "categ_sc": [   ("mhteam","BU Customer Success/Sales/SOP &nbsp;"),
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
        escalation_target = staging_dict["mhtarget"].strip().lower()
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
forms = {
    "l1": sbpre + ["ret"] + ["l1op"] + scntxt + ["blurbtask"], #convert to task
    "cst": sbpre + ["custop"] + spr + gpt + scntxt+ ["ret"], #send to cust
    "exsc": sbpre + ["extop"] + spr + meta + sc + gpt + scntxt+ ["ret"], #prep esc via sc
    "exold": sbpre + ["extop"] + spr + meta + gpt + scntxt+ ["ret"], #customer update while in escalation
    "ex": sbpre + ["extop"] + spr + meta + scntxt + ["ret"], #escalate but no pr
    "exjira": sbpre + ["extop"] + spr + meta + jira + gpt + scntxt+ ["ret"], #prep esc to saas
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
    exclusion_list = spr + gpt
    nvalue = list(filter(lambda x: x not in exclusion_list, sequence))
    temp_dict[nkey] = nvalue
forms.update(temp_dict)


scenarios_with_preseed = {"sum": "write to the customer after the chat conversation you just had with them. summarize the conversation skipping the less important back and forth and focusing mostly on the request and outcome."}

half_list = ["l1", "cst", "exsc", "exold", "ex", "exjira", "exeng", "exb", "l2", "clst", "clsch", "sum"] 
full_list = half_list + [item+"n" for item in half_list]

scenarios_requiring_pr = list(filter(lambda x: x not in ["clsch"], half_list))
scenarios_requiring_esc = [item for item in full_list if item.startswith("e") and not item.endswith("n") and not item in ["exb","exold"]]


def main():
    clear_terminal() #debug
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
    }
    #repopulate elements from _orig
    global elements
    for key in elements:
        elements[key] = elements_orig[key]

    pr_promptsys = "You are a customer support agent trained in responding to customers. Don't repeat yourself too much and avoid mentioning an ETA or promising resolution. Customers or internal requesters that reach out via email are either facing a technical issue or looking to get a request processed, and actioned."

    pr_prompt1 = f"""Write a response to the last message from the customer in a conversation provided to you.  Make sure of the following:
        -Use direct action oriented language.
        -Don't be overly obsequious.
        -Don't repeat yourself too much
        -Use active voice if appropriate.
        -Use a salutation like "Dear [First Name]"
        -If replying to the first message from the requestor i.e. if there are no existing replies from the support team,the first line should be: "Thank you for contacting <product> Support team. I understand ...
        -Draft a response considering the information in the clue which provides you with context on how to shape your response. You may rephrase and regurgitate the clue where it is relevant for the customer/requester. 

        I am providing the following inputs:"""

        
         
    pr_prompt2 = "Please rewrite the response basing it mostly on the clue provided earlier. If the clue indicates additional actions have happened after the Conversation, take those into consideration."

    pr_prompt3 = """Ok. Now considering the information about what to do in the clue, and also the conversation and response sent already to the customer, write to the team as relevant being mindful that:
    -you should be concise
    -state the problem and what needs to be done; don't exhort too much
    -you should be precise
    -you should use a brevity of words
    -start with "Subject:"
    -start the body with "Description:"
    -if provided in the conversation or the clue include specific details and reference numbers and names verbatim 
    -no byline
"""
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
        f_pr = firstpr_extractor(soup)
        conversation = get_zd_messages(soup,f_pr)
    else:
        print_bright("No HTML content found in clipboard. Please copy a Zendesk ticket or chat conversation and try again.",bredf)
        soup = BeautifulSoup("<html></html>", 'html.parser')
        f_pr = ""
        conversation = ""
    
    elements["byline"] =  "Best regards,\n"+ agent_name+"\nX Support Team\n"
   
    wrapped_instruction = term_print_string("What do you want to do? e.g. Close ticket no pr | Escalate to Rishap CSquery | send to saas inc:",
                                        " ")
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
        preseeded_context = ""
        response = ""

        if chosen_scenario in scenarios_requiring_pr: #debug
            if chosen_scenario in scenarios_with_preseed:
                preseeded_context = scenarios_with_preseed[chosen_scenario]
                information = ""
            else: 
                preseeded_context = ""
            #Insert product in PR PRomtp sys
            pr_prompt1 = pr_prompt1.replace("<product>", ticket_prodname,1)
            
            response = get_intuitPR(pr_model,conversation,preseeded_context,information,pr_promptsys,pr_prompt1,pr_prompt2)
            elements["intuitPR"] = response

        subjstring = "" 
        desc_string = "" 
        issuestring = ""

        if chosen_scenario in ["exb",] and not any(intent == "no_esc" for intent in intentions_list):
            issuestring = get_intuitIssue(esc_model,conversation,response,pr_promptsys)
            elements["intuitIssue"] = issuestring 
        
        if chosen_scenario in ["exb","exbn"]:
            elements["e2b"] = get_bu_esc_datatable(ticket_prodname,elements)  # func using dict 
        
        if chosen_scenario in scenarios_requiring_esc and not any(intent == "no_esc" for intent in intentions_list):
            subjstring, desc_string = get_intuitEsc(esc_model,conversation,response,elements,information,pr_promptsys,pr_prompt1,pr_prompt2,pr_prompt3) # func using dict
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
    last_term_print = term_print_string("Bookmarklet - and press Enter...", " ")
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
    


for intent, lst in intent_sets.items():
    for search_term in lst:
        if search_term.startswith(" "):
            search_term = "!" + search_term[1:]
        if search_term.endswith(" ~"):
            search_term = search_term[:-2] + "!~"
        if search_term.endswith(" "):
            search_term = search_term[:-1] + "!"
        if not search_term.startswith("!"):
            search_term = "%" + search_term
        if not search_term.endswith("!"):
            search_term = search_term + "%"
    
    search_term = search_term.replace("!","")
    
    chunks = []
    for i in range(0, len(lst), 5):
        chunk = lst[i:i + 5]
        chunks.append(chunk)
    intent_chunks = [] 
    for chunk in chunks:
        string = f"{intent}: {chunk}"
        intent_chunks.append(string)


with open("intent_list_dump.txt", "w") as f:
    for item in intent_chunks:
        f.write("%s\n" % item)

