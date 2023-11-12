##A scripting tool
# Import the pyperclip module.
import pyperclip
from openai import OpenAI
from bs4 import BeautifulSoup
import textwrap
import shutil
import sys

terminal_width = shutil.get_terminal_size().columns
subindent = " | "
available_width = terminal_width - len(subindent)
zd_messages_str = ""

def get_product(html_content,prod_dict):
    if html_content.find("<html lang") != -1:
        soup = BeautifulSoup(html_content, 'html.parser')
        all_labels = soup.find_all('label',{'class':'sc-anv20o-4 iIWDoF StyledLabel-sc-2utmsz-0 bYrRLL'})
        prod_name = "No prod YET"
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
    
#def scenario_extractor(input_string):
#    
#    all_scenarios = ["basic", "tsk", "cst", 
#                     "ex", "exsaas", "exold", 
#                     "exn", "exb", "excf", "exbn", 
#                     "exbz", "l2", "l2n", "l1n", 
#                     "clst", "clsth", "clstn", "clsch"]
#    
#    no_pr = ["basic", "tsk", "exn", "l2n", "l1n", "clstn"]
#    yes_pr = ["ex", "exsaas", "exold", "exb", "excf", "exbn", "exbz", "l2", "clst", "clsth"]
#    esc = ["ex", "exsaas", "exold", "exn", "exb", "exbn", "exbz", "excf"]
#    no_esc = ["basic", "tsk", "l2n", "l1n", "clstn"] 

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
    if start_idx != -1:
        return string[:start_idx] #Also removes message history after byline
    else:
        return string

def get_zd_messages(html_content):  
    zd_messages = []
    soup = BeautifulSoup(html_content, 'html.parser')

    class_kandy = 'sc-1o8vn6d-0 fcCUeL'
    class_kandy2 = 'sc-5rafq2-0 gEMoXX'
    class_kandy3 = 'sc-1m2sbuc-1 glubzr'
    class_chat = 'sc-wv3hte-1 epkhmy'
    class_chat2 = 'sc-wv3hte-0 eKImJ'

    for div in soup.find_all('div', {'class': ['sc-54nfmn-1 bthKwz','sc-1qvpxi4-1 lvXye','sc-i0djx2-0 fwLKxM',class_kandy2,class_chat,class_chat2]}):
        if div is None:
            print("No div") 
        else:
        # Get the Name
            sender_name = "No name"
            for title in div.find_all_previous('div', {'class': ['sc-1gwyeaa-2 icjiLH','sc-yhpsva-1 dtIjfP']}):
                strong_text = title.find('strong')
                if strong_text:
                    sender_name = strong_text.text.strip()
                    if sender_name.find(" "):
                        sender_name = sender_name.split()[0]
                    break
        # Get the Comment      
            comment_div = div.find('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2]})
            comment_text = "No comment"
            if comment_div is not None:
                comment_text_pre = comment_div.text[:2000]
                comment_text = bylinestripper(comment_text_pre)
            if comment_text != "No comment":
                print(" "+sender_name + ": ") 
                wrapped_comment = textwrap.fill(comment_text, 
                                                width=available_width,
                                                initial_indent=subindent,
                                                subsequent_indent=subindent,
                                                )
                print(wrapped_comment+"\n")
                zd_messages.append(f"{sender_name}: \n | {comment_text}")

    zd_messages_str = "\n".join(zd_messages)

#Add a feature to scrape the first message if it is an IN. Not tested yet.
    first_IN = ""
    for div in soup.find_all('div', {'class':'sc-1wvqs23-0 dTcJJt'}):
        if div is None:
            print("No div when looking for first IN ATTENTION")
        else:
            all_comments = div.find_all_next('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled']})
            if all_comments:
                for comment in all_comments:   
                    first_comment =  comment.text
                    first_IN = first_comment
                    break
            strong_text = div.find('strong')
            sender_name = "No name"
            if strong_text:
                sender_name = strong_text.text
            first_IN = sender_name + ": \n " + "| " + first_comment
        break
#Debug    if first_IN[:50] == zd_messages_str[:50]:

    if zd_messages_str[:50] != first_IN[:50]:
        zd_messages_str = first_IN + "\n" + zd_messages_str
    
    return zd_messages_str[-7000:]

def get_intuitPR(conversation,dictname,preseeded_context):
    client = OpenAI()
    if preseeded_context != "":
        information = preseeded_context
    else:
        information = input("Clue:")
    completion = client.chat.completions.create(
      model="gpt-4-1106-preview",
      messages=[
        {"role": "system", "content": "You are a customer support agent trained in responding to customers without promising resolution. If appropriate you can give them some assurance that their issue or request is being handled. Customers that reach out via email are either facing a technical issue or looking to get a request processed, and actioned."},
        {"role": "user", "content": f"""

    Write a response to the last message from the customer in a conversation provided to you.  Make sure of the following:
    -Be direct and use action oriented language.
    -Don't be too wordy.
    -Use a salutation like "Dear [Customer's First Name]"
    -Only if there are no messages from the support team, and only messages from bots or customers,he first line should be Thank you for contacting [Product] Support team. I understand ...
    -There should be no byline.
    -The meat and bones of the reply should be based on the information provided to you as input. Draft a response considering that information and regurgitating it if appropriate.

    I am providing the following information

    Conversation: {conversation}
    Information: {information}
    """}
      ]
    )
    string = str(completion.choices[0].message.content)
    string = bylinestripper(string) 
    dictname["intuitPR"] = string
    
def get_intuitEsc(conversation,response,dictname):
    client = OpenAI()
    subject = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role":"system","content": "You are a customer support agent trained in handling customer issues, for which you have to create work units for the finance and other teams within the company"},
                {"role":"user","content": f"""considering the conversation and response sent already to the customer, prepere an escalation to the finance or other team as relevant, being mindful that:
-you should be concise
-you should be precise
-you should use a brevity of words
-start with "Subject:"
-start the body with "Description:
-no byline"
Here is the conversation: {conversation}
Here is the response: {response}"""}
                ]
            )
    string = str(subject.choices[0].message.content)
    start_idx = string.find("Subject:")+8
    end_idx = string.find("Description:")
    if start_idx != -1 and end_idx != -1:
        subj_string = string[start_idx:end_idx]
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
}

#define a function to modify the final string
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

# Define a function to iterate over list and extract the values, then do lookup by key and print values
def pscenario(scenario,product):
    vallist = []
    for ndex in scenario:
        value = elements[ndex]
        vallist.append(value)
    return "\n".join(vallist)
    
#Find "Support Team" in finalstring1 and insert product name before it
#    finalstring2 = finalstring1.replace("Support Team", products.get(product,"Product Err") + " Support Team")
#find [Jira link] in finalstring2 and insert the value from dictionary jira_links after it in the brackets
#    finalstring = finalstring2.replace("[Jira link]", "[Jira link](" + jira_links[product] + ")")
#    print(finalstring)
#    pyperclip.copy(finalstring)

   
# Define the scenarios using only the elements defined above

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
    "clsch": sbpre + ["clscop"], #Close chat
    "qc": ["scrapedPR"],
    "sum": ["intuitPR"],
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
                "exbz":"BU Customer Success/Sales/SOP",
                "exb":"BU Other",
                "excf":"Central Finance",
                "exbn": ""}

scenarios_with_preseed = {"sum": "Summarize the conversation skipping the less important back and forth and focusing on the request and outcome. Don't reassure too much"}

scenarios_requiring_pr = ["cst", "ex", "exsaas", "exold", "exb", "excf", "exbz","l2", "clst", "clsth","qc", "sum"]
scenarios_requiring_esc = ["ex", "exsaas", "exb", "excf", "exbz"]
scenarios_requiring_bzjira = ["exbz"]
scenarios_requiring_cfjira = ["excf"]


def main():
    sep = " "+"-"*(terminal_width-2)
    print(sep)
    html_content = pyperclip.paste()
    conversation = get_zd_messages(html_content)
    print_blurblist = []
    for key,value in scenarios.items():
        if str(key).endswith("n") is False:
            print_blurblist.append(str(key) + " - " + scenario_definitions[key])
    for text in print_blurblist:
        print(text)
    print(sep+"\nPick one:")
    chosen_scenario = input()
    if chosen_scenario in ["","quit"]: 
        print("Goodbye!")
        sys.exit()
    elif chosen_scenario in scenarios:
        ticket_productcode, ticket_prodname = get_product(html_content,products)
        if chosen_scenario in scenarios_requiring_pr:
            if chosen_scenario in scenarios_with_preseed:
                preseeded_context = scenarios_with_preseed[chosen_scenario]
            else: 
                preseeded_context = ""
            get_intuitPR(conversation,elements,preseeded_context)
            response = elements["intuitPR"]
        if chosen_scenario in scenarios_requiring_esc:
            get_intuitEsc(conversation,response,elements)
        finalstring = pscenario(scenarios[chosen_scenario],ticket_productcode)
        finalstring = modifystring(finalstring,chosen_scenario,ticket_productcode,ticket_prodname)
        idx_link_end = finalstring.find("2jr)_\n")+len("2jr)_\n")+1
        finalstring_sub = finalstring[idx_link_end:-2].replace("**","").replace("&nbsp;","")
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
                                        width=terminal_width-2,
                                        initial_indent=" ",
                                        subsequent_indent=" ",
                                    )
            fs_sub_paras_clean.append(wrapped_para)
        fs_sub_clean = "\n\n".join(fs_sub_paras_clean)
        fs_sub_clean = fs_sub_clean.replace("\n [rl]"," ")
        sep2 = u'\u2554'+u'\u2550'*(terminal_width-2)+u'\u2557'
        sep3 = u'\u255A'+u'\u2550'*(terminal_width-2)+u'\u255D'
        print(sep2)
        print(fs_sub_clean)
        print(sep3)
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
