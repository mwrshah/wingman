##A scripting tool
# Import the pyperclip module.

import pandas as pd
import pyperclip
from openai import OpenAI
from bs4 import BeautifulSoup
import textwrap
import shutil
import sys
import os
from termcolor import colored


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


#Global scope vars for printing
terminal_width = shutil.get_terminal_size().columns
subindent = " | "
available_width = terminal_width - len(subindent)

#Global scope vars for ZD scraping
zd_messages_str = ""
class_kandy = 'sc-1o8vn6d-0 fcCUeL'
class_kandy2 = 'sc-5rafq2-0 gEMoXX'
class_kandy3 = 'sc-1m2sbuc-1 glubzr'
class_chat = 'sc-wv3hte-1 epkhmy'
class_chat2 = 'sc-wv3hte-0 eKImJ'
# Too generic gets PRs and INs class3 = 'sc-ocla5p-2 inrRJ'
comment_text = ""
first_commentorIN = ""
sender_name = "John Doe"

def print_wrapped(string,color):
     wrapped_string = textwrap.fill(string, width = terminal_width-4, initial_indent = "    ", subsequent_indent = "    ")
     print_bright(wrapped_string,color)

def printlogo():
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

    print_bright(textwrap.fill("Wingman v0",
                               terminal_width-10)
                                .rjust(terminal_width-4),whitef)

#TAPE - Getting first comment from regular PR classes
def firstpr_extractor(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    comment_text = ""
    for div in soup.find_all('div', {'class': ['sc-54nfmn-1 bthKwz','sc-1qvpxi4-1 lvXye','sc-i0djx2-0 fwLKxM',class_kandy2,class_chat,class_chat2]}):
        if div is None:
            print("No div")
        else:
            comment_div = div.find('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2]})
            if comment_div:
                comment_text_pre = comment_div.text[:2000]
                comment_text = bylinestripper(comment_text_pre)
            break
    return comment_text

def print_bright(message, color_code):
    print(f"{color_code}{message}{resetf}")


def get_product(html_content,prod_dict):
        soup = BeautifulSoup(html_content, 'html.parser')
        all_labels = soup.find_all('label',{'class':'sc-anv20o-4 iIWDoF StyledLabel-sc-2utmsz-0 bYrRLL'})
        prod_name = "ProductHTMLsearchFailure"
        for label in all_labels:
            if label.text.find("Product*") != -1:
                prod_name = label.find_next('div', {'class': 'StyledEllipsis-sc-1u4uqmy-0 gxcmGf'}).text
                prod_name = prod_name.strip()
                break
        for key, value in prod_dict.items():
            if value == prod_name:
                productcode = key
                break 
            else:
                productcode = "error"
        return productcode, prod_name

def scenario_extractor(input_string):
    
    all_scenarios = ["tsk", "cst", 
                     "ex", "exsaas", "exold", 
                     "exn", "exb", "excf", "exbn", 
                     "exbz", "l2", "l2n", "l1n", 
                     "clst", "clsth", "clstn", "clsch"
                     "qc","sum"]
       #Define subsets
    scenario_subsets= {
            "quit":["quit"],
            "cls":["clst", "clsth", "clstn", "clsch"],
            "cst":["cst"],
            "l1": ["l1n"],
            "l2": ["l2", "l2n"],
            "esc":["ex", "exsaas", "exold", "exn", "exb", "exbn", "exbz", "excf","l2","l1","l2n","l1n"],
            "yes_pr":["sum","ex", "cst","exsaas", "exold", "exb", "excf", "exbn", "exbz", "l2", "clst", "clsth"],
            "no_pr":["qc", "tsk", "exn", "l2n", "l1n", "clstn","exbn"],
            "qc":["qc"],
            "task":["tsk"], 
            "sum":["sum"],
            "cf":["excf"],
            "sc":["ex"],
            "bz":["exbz"],
            "bu":["exb","exbn",],
            "chat":["clsch"],
            "clst":["clst","clstn"],
            "saas":["exsaas"],
            "in_esc_update": ["exold"],
    }
    def pbug(name,value):
        print("Printing "+name+ ": "+value+"\n")

    parse_string_full = input_string.lower().strip()
    parse_string = parse_string_full[:50]
    
    #pbug("parse_string",parse_string)
    
    gt_idx1 = parse_string.find(">")
    dot_idx1 = parse_string.find(".")
    
    #if both found
    if gt_idx1 != -1:
        gt_present = True
        end_idx1 = gt_idx1
    elif dot_idx1 != -1:
        dot_present = True
        end_idx1 = dot_idx1
    else:
        end_idx1 = 40 #40 is a random number for slicing 80% of the parse string.

    #pbug("dot_idx1",str(dot_idx1)) 
    #pbug("gt_idx1",str(gt_idx1))
    
    #second_parse_string = parse_string[end_idx1+1:]
    #gt_idx2 = second_parse_string.find(">") 
    #dot_idx2 = second_parse_string.find(".")
    #end_idx2 = None
    #if gt_idx2 != -1:
    #    end_idx2 = second_parse_string.find(">") + end_idx1+1
    #elif dot_idx2 != -1 and end_idx2 == None:
    #     end_idx2 = second_parse_string.find(".") + end_idx1+1
    #else: 
    #   end_idx2 = end_idx1 + 24 #24 is a random number. 
    #end_idx1 will never be unassigned when end_idx2 is called upon because if it is then the following block applies.


    slice1_pre = parse_string[:end_idx1]
    slice1 = " " + slice1_pre + " " #some of the search terms are defined with leading spaces so this is necessary for search term starting at the beginning of the sentence. The benefit of having space in the search term is it won't fire for term appearing within a word. Example " sc ".
    slice1 = slice1.replace(".", " .")
    
    clue = input_string[end_idx1+1:]    
    
    
    def negation_check(string):
        negations = ["don't", "not", "n't"]
        if any(string[-7:].find(word) != -1 for word in negations):
            return True
        else:
            return False

    collected_intents_dict = {} #COLLECTION OF ALL INTENTS FOUND
    
    intent_sets = {
        "quit" : ["quit", "exit"],
        "cls" : ["close", "cls"],
        "cst" : ["customer", "cust", "cst"],
        "l1" : ["l1", "level 1", "level one", "l1n"],
        "l2" : ["l2", "level 2", "level two", "l2n"],
        "esc" : ["external", "escalate", "elevate", " ext ", "send this to","send it to", "send to"],
        "yes_pr" : ["a pr ","write", "draft", "compose", "yes pr"],
        "no_pr" : ["no pr", "don't write", "no reply", "no response", "don't draft","don't draft"],
        "qc" : ["quality", " qc ","check", " chk ", "chck", " qlt",  "review",],
        "task" : ["task", "tsk"],
        "sum" : ["summary", " sumr "," sumz ", " smz ", " smry ", " sm "],
        "cf" : ["to finance"," the finan", " fin ","cf ", "central finance", "treasury", " ap ", "collect cash", "udf", "accounts pay", " rishap", "cquery", "write off", "vendor reg", "vendor pay", "o2c", "record maint", "record mn", "record man", "record mg"],
        "sc" : [" sc ","side conv", "side conversation", " ex ",],
        "bz" : ["bu jira", "business ops", " bz ", "bizops", "exbz"," account m","ount mng", " ount mg"],
        "bu" : ["elevate", "exbn", "noc ", " elvt ", " bu ", "exb"], 
        "chat": ["clsch"," chat ", " cht ",],
        "clst" : ["ticket", " tkt ", " tckt ","clst"],
        "saas" : [" saas ", " infra t", " infrastructure t", " exsaas "],
        "in_esc_update" : ["in escalation", "in esc ", "exold" ],
    }

    #Small check
    scenario_subsets_keys = list(scenario_subsets.keys())
    intent_sets_keys = list(intent_sets.keys())
    if scenario_subsets_keys != intent_sets_keys:
        print("Error: Scenario subsets and intent sets do not match"*20)  
    #Small check end

    encapsulated_terms = []
    #Small check on inclusion of one search term in another
    def encapsulated_check(term1, term2):
        if term1 in term2:
            return True
        else:
            return False
   
    #intent extractor collects the intents that match in the parsed string and stores them in a collected_intents_dict
    def intent_extractor(string, intent_sets_dict):
        if not string:
            return None
        for intent, searchtermlist in intent_sets_dict.items():
            for searchterm in searchtermlist: 
                #DEBUGpbug("intent checked ",intent)
                where_is_it = string.find(searchterm) 
                if where_is_it != -1: 
                    new_string = string[:where_is_it]
                    #pbug("new_string",new_string)
                    if not negation_check(new_string):
                        #pbug("searchterm:",searchterm)
                        #pbug("           intent",intent)
                        searchterm = searchterm
                        found_intent = intent
                        existing_encapsulated_searchterm = False
                        for term, val in collected_intents_dict.items():
                            if encapsulated_check(searchterm, term):
                                existing_encapsulated_searchterm = True 
                                break
                        if not existing_encapsulated_searchterm:
                            collected_intents_dict[searchterm] = found_intent
        return None
    
    intent_extractor(slice1,intent_sets) 
    tempintentionsets = []
    for searchterm, intent in collected_intents_dict.items():
        #print(str(searchterm)+ ":" + str(intent)) #DEBUG 
        intent_subset = set(scenario_subsets[intent])
        tempintentionsets.append(intent_subset) 
        #pbug("tempintentionsets",str(tempintentionsets))
    
    if tempintentionsets: 
        intersectionset = tempintentionsets[0]
        #pbug("intersectionset",str(intersectionset))
    else:
        intersectionset = set()
    
    for current_set in tempintentionsets[1:]:
        intersectionset &= current_set
        #pbug("intersectionset",str(intersectionset))
    
    lookuplist = list(intersectionset)
    #print_wrapped("lookuplist"+str(lookuplist),magf) #DEBUG 
    #pbug("slice1",slice1)
    #pbug("slice2",slice2)
    #pbug("clue",clue)


    flowbreak1 = "You need to tell Wingman what you intend to do AND give a clue e.g. Escalate to BU no PR. We need approval from account management to proceed"
    flowbreak2 = "Wingman is confused about what you want to do.\n Try being more specific"
    wrapped_flowbreak1 = textwrap.fill(flowbreak1, width = terminal_width-4, initial_indent = "    ", subsequent_indent = "    ")
    wrapped_flowbreak2 = textwrap.fill(flowbreak2, width = terminal_width-4, initial_indent = "    ", subsequent_indent = "    ")
    
#Start Section - Get the intents to pass through in return
    #REF: quit, cls, cst, l1, l2, esc, yes_pr, no_pr, qc, task, sum, cf, sc, bz, bu, chat, clst, saas, in_esc_update
    unique_intents = []
    for key, value in collected_intents_dict.items():
        if value not in unique_intents:
            unique_intents.append(value)
    for intent in unique_intents:
        print_bright(" "+intent,whitef)
    if len(lookuplist) == 0:
        print(wrapped_flowbreak1)     
    elif len(lookuplist) > 1:
        lookuplist = [scenario for scenario in lookuplist if not scenario.endswith("n")]
        if len(lookuplist) > 1:
            print(wrapped_flowbreak2)
    if len(lookuplist) > 1:
        return None, clue
    elif len(lookuplist) == 0:
        return None, clue
    elif len(lookuplist) == 1:
        print(f"{yellowf}Running scenario: {resetf}"+f"{bredf}{lookuplist[0]}{resetf}")
        return lookuplist[0], clue 

#def scenario_extractor(input_string):
#    scenario = ""
#    input_string_orig = input_string
#    input_string = input_string_orig.lower().strip()
#    input_string = input_string[:100]
#    idx_stop = input_string.find(".")
#    if idx_stop == -1:
#        idx_stop = input_string.find(">")
#    if idx_stop != -1:
#        input_string = input_string[:idx_stop]
#    else:
#        input_string = input_string[:30]
#    input_string = input_string.replace(".", " .")
#    input_string = input_string.replace(">", " >")
#    lookuplist = input_string.split()
#    all_scenarios = ["tsk", "cst",
#                     "ex", "exsaas", "exold",
#                     "exn", "exb", "excf", "exbn",
#                     "exbz", "l2", "l2n", "l1n",
#                     "clst", "clsth", "clstn", "clsch",
#                     "qc","sum","","quit"]
#    found_words = []
#    for word in lookuplist:
#        if word in all_scenarios:
#            scenario = word
#            break
#        else:
#            scenario = ""
#            print("Error: Scenario not found")
#    if scenario[:2] in ["ex","l2"]:
#        clue = input_string_orig.replace("no pr", "")
#        clue = clue.replace("pr", "")
#    elif scenario == "exsaas":
#        clue = input_string_orig.replace({found_word}, "")
#    clue = input_string_orig[idx_stop+1:]
#    return scenario, clue



def bylinestripper(string):
    start_idx = string.find("Warm regards,")
    if start_idx == -1:
        start_idx = string.find("Best regards,")
    if start_idx == -1:
        start_idx = string.find("Regards,")
    if start_idx == -1:
        start_idx = string.find("Sincerely,")
    if start_idx == -1:
        start_idx = string.find("Kind regards,")
    if start_idx == -1:
        start_idx = string.find("Thanks,")
    if start_idx != -1:
        return string[:start_idx-1] #Also removes message history after byline
    else:
        return string

def jiralinkstripper(string):
    start_idx = string.find("[Jira link]")   
    end_idx = string.find("/issues)")
    if start_idx != -1 and end_idx != -1:
        start_idx = start_idx+len("[Jira link]") 
        end_idx = end_idx+len("/issues)")
        return string[:start_idx] + string[end_idx:] 
    else:
        return string

def BUelevationsripper(string):
    start_idx = string.find("| Issue")   
    end_idx = string.find("we escalating?) ")
    if start_idx != -1 and end_idx != -1:
        start_idx = start_idx-1
        end_idx = end_idx+len("/we escalating?) ")+7
        alt_string = """
    Issue summary:
    Reproduction steps:
    Current behaviour:
    Expected behaviour:
    Troubleshooting steps:
    Reason for escalation (What should BU do?):
    Justification for escalation:""" 
        string_after = string[:start_idx] + alt_string + string[end_idx:] 
        return string_after

    else:
        return string
def get_zd_messages(html_content,f_pr):  
    zd_messages = []
    soup = BeautifulSoup(html_content, 'html.parser')
    messagecounter = []

#Add a feature to scrape the first message if it is an IN
    first_IN = ""
    first_IN_pre = ""
    first_commentorIN = ""
    sender_name = "John Doe"
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

            first_IN = sender_name+ ": \n " + "| " + first_IN_pre
#            print("\nfirst_IN: \n" + first_commentorIN[:50])
#            print("\nfirst_pr: \n' " + f_pr[:50])
            break

    if first_commentorIN[:50] != f_pr[:50]:
        print("\n Making SURE to print first IN as it is different from the inclusion in messages \n")
        print_bright(" "+sender_name + ": ",whitef)
        wrapped_comment = textwrap.fill(first_IN_pre, 
                                        width=available_width,                                        
                                        initial_indent=subindent,
                                        subsequent_indent=subindent,
                                        )
        print_bright(wrapped_comment+"\n",yellowf)

    for div in soup.find_all('div', {'class': ['sc-54nfmn-1 bthKwz','sc-1qvpxi4-1 lvXye','sc-i0djx2-0 fwLKxM',class_kandy2,class_chat,class_chat2]}):

        if div is None:
            print("No div") 
        else:
            sender_name = "No name"
            for title in div.find_all_previous('div', {'class': ['sc-1gwyeaa-2 icjiLH','sc-yhpsva-1 dtIjfP']}):
                strong_text = title.find('strong')
                if strong_text:
                    sender_name = strong_text.text.strip()
                    if sender_name.find(" "):
                        sender_name = sender_name.split()[0]
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
            comment_div = div.find('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2]})
            comment_text = "No comment"
            if comment_div is not None:
                comment_text_pre = comment_div.text[:2000]
                comment_text = bylinestripper(comment_text_pre)
            if comment_text != "No comment":
                print_bright(" "+sender_name + ": ",whitef)
                wrapped_comment = textwrap.fill(comment_text, 
                                                width=available_width,
                                                initial_indent=subindent,
                                                subsequent_indent=subindent,
                                                )
                #if counter is an even number
                if index == 1: 
                    print_bright(wrapped_comment,yellowf)
    #                elif index == 1:
    #                    print_bright(wrapped_comment+"\n",yellowf)
    #                elif index == 3:
    #                    print_bright(wrapped_comment+"\n",magf)
    #                elif index == 4:
    #                    print_bright(wrapped_comment+"\n",greenf)
    #                elif index % 2 != 0:
    #                    print_bright(wrapped_comment+"\n",bredf)
                else:
                    print_bright(wrapped_comment,bcyanf)
                zd_messages.append(f"{sender_name}: \n | {comment_text}")

    zd_messages_str = "\n".join(zd_messages)
    if first_commentorIN[:50] == f_pr[:50] and len(zd_messages_str) > 100:
        zd_messages_str = zd_messages_str[-7000:]
    else:
        zd_messages_str = first_IN + "\n" + zd_messages_str[-7000:]
    
    with open("/Users/munawarali/Documents/Scripter/print_zd_messages.txt", "w") as f:
        f.write("ZD MESSAGES including FIRST IN: \n\n" + zd_messages_str)
    with open("/Users/munawarali/Documents/Scripter/print_zd_messages.txt", "a") as f:
        f.write("\n\n\n\n\n\nfirst_IN FOUND: \n" + first_IN)
    return zd_messages_str


pr_promptsys = "You are a customer support agent trained in responding to customers. If appropriate you can give them some assurance that their issue or request is being handled, but don't repeat yourself too much or commit ETAs. Customers that reach out via email are either facing a technical issue or looking to get a request processed, and actioned."

pr_prompt1 = f"""Write a response to the last message from the customer in a conversation provided to you.  Make sure of the following:
    -Use direct action oriented language.
    -Don't repeat yourself too much
    -Use active voice if appropriate.
    -Use a salutation like "Dear [First Name]"
    -If replying to the first message from the requestor if there are no existing replies from the support team,the first line should be: "Thank you for contacting [Product] Support team. I understand ...
    -Draft a response considering the information in the clue which provides you with context on how to shape your response. You may regurgitate information from the clue if it is appropriate.

    I am providing the following inputs:"""

    
     
pr_prompt2 = "Please rewrite the response basing it mostly on the clue provided earlier. If the clue indicates additional actions have happened after the Conversation, take those into consideration."

pr_prompt3 = """Ok. Now considering the information about what to do in the clue, and also the conversation and response sent already to the customer, write to the finance or other team as relevant to ask for help, being mindful that:
-you should be concise
-you should be precise
-you should use a brevity of words
-start with "Subject:"
-start the body with "Description:"
-be sure to include specific details like phone numbers and emails and invoice numbers if provided in the conversation or the clue
-no byline
"""

#DOUBLECHECK THIS HERE
def get_intuitPR(conversation,dictname,preseeded_context,seededclue):
    client = OpenAI()
    if preseeded_context != "":
        clue = preseeded_context
    else:
        clue = seededclue
    global pr_promptsys
    global pr_prompt1
    global pr_prompt2
#gpt-4-1106-preview
    print("Processing clue: " + clue[:40])
    #print("Processing conversation: " + conversation[:40])
    #print("Processing preseeded_context: " + preseeded_context[:40])
    #print("Processing pr_prompt1: " + pr_prompt1[:40])
    #print("Processing pr_promptsys: " + pr_promptsys[:40])
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
      
        messages=[
        {"role": "system", "content": pr_promptsys},
        {"role": "user", "content": pr_prompt1 + "Conversation:\n" + conversation + "Clue:\n" + clue},
        #{"role": "assistant", "content": "<response redacted>"},
        #{"role": "user", "content": pr_prompt2},
        ]
    )
    
    string = str(completion.choices[0].message.content)
    string = bylinestripper(string) 
    dictname["intuitPR"] = string
    
def get_intuitEsc(conversation,response,dictname,clue):
    client = OpenAI()
    global pr_promptsys
    global pr_prompt1
    subject = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role":"system","content": pr_promptsys +"Sometimes have to reach out to the finance and other teams within the company, to ask them for information, or help"},
                {"role":"user","content": pr_prompt1 + "Conversation:\n" + conversation + "Clue:\n" + clue},
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
    dictname["prepesc2"] = "**Subject:** &nbsp;" + subj_string
    start_idx2 = string.find("Description:")+12
    if start_idx2 != -1:
        desc_string = string[start_idx2:]
    else:
        desc_string = string
    dictname["prepesc3"] = "**Description:** &nbsp;\n" + desc_string + "\n"

products = {
    "vd": "Volt Delta",
    "exinda": "GFI - Exinda Network Orchestrator",
    "ssmart": "StreetSmart",
    "ffm": "Field Force Manager",
    "pb": "Playbooks",
    "bonzai": "Bonzai Intranet",
    "firstrain": "Firstrain",
    "lg": "GFI - LanGuard",
    "evmgr": "GFI - Eventsmanager",
    "xinet": "Northplains - Xinet",
    "kandy": "Kandy",
    "alp": "ALP",
    "kc": "Kayako Classic",
    "jvhop": "Jive HOP",
    "tnk": "Kayako",
    "streetsmart": "StreetSmart",
    "kayakoclassic": "Kayako Classic",
    "jvcld": "Jive Cloud",
    "mob": "Mobilogy Now",
    "cf": "Central Finance",
    "ans": "AnswerHub",
    "acrm": "ACRM",
    "ev": "Everest",
    "bz": "Ignite BizOps", 
    "sky": "Skyvera Analytics",
    "sky5g": "Skyvera Network 5G & WiFi",
    "acorn": "Acorn",
    "l3" : "Learn and Earn",
    }


# Define dict with Jira links
jira_links = {
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
    "sky": "no Jira",
    "sky5g": "no Jira",
    "l3" : "no Jira",
    }
 

#Define the individual elements of format that can be remixed in scenarios
elements = {
#Main elements
    "instlink": "_[Instructions](https://docs.google.com/document/d/1w6pg-Lqz1Y5n8Gah7JXTRAnNEgnLGDgQn0p4EE_DdyU/edit#bookmark=id.bazq9xp2u2jr)_\n",
    "action": "**What is your proposed action?** &nbsp;",
    "custop": "* Send to customer\n",
    "l2op": "* Send to L2\n",
    "extop": "* Send to external team\n",
    "clstop": "* Close ticket\n",
    "l1op": "* Send to L1\n",
    "buop": "* Elevate to BU\n",
    "clscop": "* Close chat\n",
    "divider": "---",
    "pr": "**PR**\n",
    #insert product name from prod dict
    "byline": "Best regards,\nMunawar Shah\n" +"X Support Team\n",
    "context": "**Additional context?** \n",
    "gpt": "**GPT**&nbsp;",
    "gptyes": "_Did you use GPT?_ Yes.\n",
    "gptno": "_Did you use GPT?_ No. Not required\n",
#Adding sometimes used elements
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
#Pieces of ZD metadata escalation
    "mxteam": "**External Team:** &nbsp; ",
    "mhreason": "**On Hold Reason:** &nbsp;",
    "mhtimer": "**On Hold Timer:** &nbsp; &nbsp; ",
    "mhtarget": "**Escalation Target:** &nbsp; &nbsp; \n",
    #Options for mxteam
    "mxteam1": "BU Customer Success/Sales/SOP",
    "mxteam2": "Saas Ops",
    "mxteam3": "Internal",
    "mxteam4": "External to ESW",
    "mxteam5": "Engineering",
    "mxteam6": "Crossover HR",
    "mxteam7": "Crossover Finance",
    "mxteam8": "Central Finance",
    "mxteam9": "BU PS",
    "mxteam10": "BU Other",
    #add two empty lines after above line
    "ret": "\n",    
    #Add the SC options
    "sc1": "**SC**&nbsp;",
    "sc2": "**Subject:**&nbsp;NA",
    "sc3": "**Description:**&nbsp;\n",
    "sc4": "**Attachments:**&nbsp; NA\n",
    #Pieces of Jira escalation
#Insert Jira link from jira_links dict
    "jirabiz": "[Jira link]",
    "prepesc1": "**Issue Type:** Task\n",
    "prepesc2": "**Subject:** &nbsp;NA\n",
    "prepesc3": "**Description:** &nbsp;\n",
    "prepesc4": "**Zendesk Ticket IDs:** &nbsp;\n",
    "prepesc5": "**Attachments:** &nbsp;\n",
    "prepesc6": "**Unit Type:** &nbsp;\n",    
    "intuitPR": "",
    "scrapedPR": "scraped_PR",
    "sumspace": "     ",
    "clschspace": " ",
}

#Define a rich text table for escalate to BU
datatable = { "Issue Summary": ["Reproduction Steps", 
                                "Current Behaviour",
                                "Expected Behaviour",
                                "Troubleshooting Steps",
                                "Reason for Escalation (What do we want the BU to do?)",
                                "Justification for Escalation(Why are we escalating?)"],
             " " : [" "," "," "," "," "," "]
             }
df = pd.DataFrame(datatable) 
df_cp = df.to_markdown(index=False)

elements["e2b"] = df_cp+"\n"


def remix_elements(scenario,product):
    vallist = []
    for element_name in scenario:
        element_value = elements[element_name]
        vallist.append(element_value)
    return "\n".join(vallist)


def modifystring(string, scenario,productcode,prodname):
    string = string.replace("X Support Team", products.get(productcode,prodname) + " Support Team")
    if scenario in scenarios_requiring_bzjira:
        string = string.replace("[Jira link]", "[Jira link](" + jira_links["bz"] + ")")
    elif scenario in scenarios_requiring_cfjira:
        string = string.replace("[Jira link]", "[Jira link](" + jira_links["cf"] + ")")
    else:
        string = string.replace("[Jira link]", "[Jira link](" + jira_links.get(productcode,"no jira found") + ")")
    string = string.replace("**External Team:** &nbsp; ", "**External Team:** &nbsp; " + scenario_ext.get(scenario,""))
    string = string.replace("**On Hold Reason:** &nbsp;", "**On Hold Reason:** &nbsp; " + scenario_reason.get(scenario,""))
    string = string.replace("**On Hold Timer:** &nbsp; &nbsp; ", "**On Hold Timer:** &nbsp; &nbsp; " + scenario_timer.get(scenario,""))
    string = string.replace("**Escalation Target:** &nbsp; &nbsp; \n", "**Escalation Target:** &nbsp; &nbsp; " + scenario_target.get(scenario,"") + "\n")
    string = string.replace("[Product]", products.get(productcode,""))
    return string
   

   
#Building the printable for remix_elements

sbpre = ["instlink","action"]
scntxt = ["divider", "context"]
spr = ["pr", "intuitPR", "byline"]
sdvdr = ["divider"]
gpt = ["divider", "gpt", "gptyes"]
meta = ["mxteam", "mhreason", "mhtimer", "mhtarget"]
jira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4", "prepesc5", "prepesc6"]
cjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc6", "prepesc4", "prepesc5"]
sjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4"]
sc = ["sc1", "prepesc2","prepesc3","sc4"]

scenarios = {
    "tsk": sbpre + ["l1op"] + scntxt + ["blurbtask"], #Convert to task
    "cst": sbpre + ["custop"] + sdvdr + spr + gpt + scntxt+ ["ret"], #Send to cust
    "ex": sbpre + ["extop"] + sdvdr + spr + meta + sc + gpt + scntxt+ ["ret"], #Prep esc via SC
    "exsaas": sbpre + ["extop"] + sdvdr + spr + meta + sjira + gpt + scntxt+ ["ret"], #Prep esc to Saas
    "exold": sbpre + ["extop"] + sdvdr + spr + meta + gpt + scntxt+ ["ret"], #Customer Update while in escalation
    "exn": sbpre + ["extop"] + meta + scntxt + ["ret"]+ ["ret"], #Escalate but no PR
    "exb": sbpre + ["extop"] + ["buop"] + sdvdr + spr + meta + ["e2b"] + gpt +scntxt + ["blurbbu"]+ ["ret"], #Elevate to BU
    "excf": sbpre + ["extop"] + sdvdr + spr + meta + cjira + gpt + scntxt+ ["ret"], #Prep esc to CF
    "exbn": sbpre + ["extop"] + ["buop"] + scntxt + ["blurbbu", "e2b"], #Elevate to BU but no PR
    "exbz": sbpre + ["extop"] + sdvdr + spr + meta + jira + gpt + scntxt+ ["ret"], #Prep esc to BU Jira
    "l2": sbpre + ["l2op"] + sdvdr + spr + gpt + scntxt+ ["ret"], #Send to L2
    "l2n": sbpre + ["l2op"] + scntxt + ["ret"], #Send to L2 but no PR
    "l1n": sbpre + ["l1op"] + scntxt + ["ret"], #Send to L1 but no PR
    "clst": sbpre + ["clstop"] + sdvdr + spr + gpt + scntxt + ["ret"], #Close ticket
    "clstn": sbpre + ["clstop"] + scntxt + ["ret"], #Close ticket but no PR 
    "clsch": ["sumspace"] +sbpre + ["clscop","clschspace"], #Close chat
    "qc": ["scrapedPR"],
    "sum": ["sumspace","intuitPR","byline"],
    }

scenario_definitions = {"tsk": "Convert to task", "cst" :"Send to customer",
                        "ex":"Prep esc via SC","exsaas":"Prep esc to Saas",
                        "exold":"Customer Update while in escalation","exb":"Elevate to BU",
                        "excf":"Prep esc to CF","exbz":"Prep esc to BU Jira",
                        "l2":"Send to L2","clst":"Close ticket" ,"clsch":"Close chat",
                        "qc":"Scrape PR","sum":"Summarize the conversation"
                        }


#Define the external team with scenarios
scenario_ext = {"ex":"Internal", 
                "exsaas":"Saas Ops",
                "exn":"Central Finance",
                "exold":"BU Customer Success/Sales/SOP",
                "exbz":"BU Customer Success/Sales/SOP",
                "exb":"BU Other",
                "excf":"Central Finance",
                "exbn": "BU Customer Success/Sales/SOP"}

scenario_reason = {"ex":"SC",
                "exsaas":"SaaS Ops Jira linked",
                "exn":"CFIN Jira",
                "exold":"CFIN Jira",
                "exbz":"BU Jira",
                "exb":"Awaiting elevation",
                "excf":"CFIN Jira",
                "exbn": "Awaiting elevation"}


scenario_timer = {"ex":"48",
                "exsaas":"9999",
                "exn":"9999",
                "exold":"9999",
                "exbz":"168",
                "exb":"4",
                "excf":"9999",
                "exbn": "4"}


scenario_target = {"ex":"Other",
                "exsaas":"Other",
                "exn":"Central Finance",
                "exold":"Central Finance",
                "exbz":"BU",
                "exb":"BU",
                "excf":"Central Finance",
                "exbn": "BU"}

scenarios_with_preseed = {"sum": "Write to the customer after the chat conversation you just had with them. Summarize the conversation skipping the less important back and forth and focusing mostly on the request and outcome."}

scenarios_requiring_pr = ["cst", "ex", "exsaas", "exold", "exb", "excf", "exbz","l2", "clst", "clsth","qc", "sum"]
scenarios_requiring_esc = ["ex", "exsaas", "exb", "excf", "exbz"]
scenarios_requiring_bzjira = ["exbz"]
scenarios_requiring_cfjira = ["excf"]


def main():
    sep = " "+"-"*(terminal_width-2)
    print(sep)
    printlogo()
    print("-"*(terminal_width-2))
    html_content = pyperclip.paste()
    f_pr = firstpr_extractor(html_content)
    conversation = get_zd_messages(html_content,f_pr)
    print_blurblist = []
#    for key,value in scenarios.items():
#        if str(key).endswith("n") is False:
#            print_blurblist.append(str(key) + " - " + scenario_definitions[key])
#    for text in print_blurblist:
#        print(" "+text)
    wrapped_instruction = textwrap.fill("What do you want to do? Also, please give wingman a clue (e.g. Close ticket > This is resolved):",
                                        width=terminal_width-4,
                                        initial_indent=" ",
                                        subsequent_indent=" ",
                                        )
    print("\n")
    print_bright(wrapped_instruction,greenf)
    print(sep)
    chosen_scenario = "" 
    while not chosen_scenario:
        user_input = input(" ")
        chosen_scenario, information = scenario_extractor(user_input) 
    if chosen_scenario in ["","quit"]: 
        print_bright(" Goodbye!",magf)
        sys.exit()
    elif chosen_scenario in scenarios:
        ticket_productcode, ticket_prodname = get_product(html_content,products)
        if chosen_scenario in scenarios_requiring_pr:
            if chosen_scenario in scenarios_with_preseed:
                preseeded_context = scenarios_with_preseed[chosen_scenario]
                information = ""
            else: 
                preseeded_context = ""
            get_intuitPR(conversation,elements,preseeded_context,information)
            response = elements["intuitPR"]
        if chosen_scenario in scenarios_requiring_esc:
            get_intuitEsc(conversation,response,elements,information)
        finalstring = remix_elements(scenarios[chosen_scenario],ticket_productcode)
        finalstring = modifystring(finalstring,chosen_scenario,ticket_productcode,ticket_prodname)
        idx_link_end = finalstring.find("2jr)_\n")+len("2jr)_\n")+1
        if idx_link_end != -1:
            finalstring_sub = finalstring[idx_link_end:-2]
        else:
            finalstring_sub = finalstring
        finalstring_sub = finalstring_sub.replace("**","").replace("&nbsp;","")
        finalstring_sub = BUelevationsripper(finalstring_sub)
        finalstring_sub = jiralinkstripper(finalstring_sub)
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
        for para in fs_sub_paras_nlpreserve:
            wrapped_para = textwrap.fill(para, 
                                        width=terminal_width-1,
                                        initial_indent=u'\u2551'+" ",
                                         subsequent_indent=u'\u2551'+" ",
                                    )
            fs_sub_paras_clean.append(wrapped_para)
        fs_sub_clean = "\n║ \n".join(fs_sub_paras_clean)

        fs_sub_clean = fs_sub_clean.replace("\n║ [rl]","")
        sep2 = u'\u2554'+u'\u2550'*(terminal_width-2)+u'\u2557'
        sep3 = u'\u255A'+u'\u2550'*(terminal_width-2)+u'\u255D'
        print_bright(sep2,magf)
        print_bright(fs_sub_clean,magf)
        print_bright(sep3,magf)
        pyperclip.copy(finalstring)

    else:
        print("Scenario is not defined")



main()

#double_line_horizontal = u'\u2550' # '═'
#double_line_vertical = u'\u2551' # '║'
#top_left_corner = u'\u2554' # '╔'
#top_right_corner = u'\u2557' # '╗'
#bottom_left_corner = u'\u255A' # '╚'
#bottom_right_corner = u'\u255D' # '╝'
