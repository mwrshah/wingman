##A scripting tool
# Import the pyperclip module.
import pyperclip
from openai import OpenAI
from bs4 import BeautifulSoup

zd_messages_str = ""
def get_zd_messages():
    zd_messages = []
    html_content = pyperclip.paste()
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
                    sender_name = strong_text.text
                    break
        # Get the Comment      
            comment_div = div.find('div', {'class': ['zd-comment','zd-comment zd-comment-pre-styled',class_chat,class_chat2]})
            comment_text = "No comment"
            if comment_div is not None:
                comment_text = comment_div.text[:2000]
            #print(comment_div)
            zd_messages.append(f"{sender_name}: \n Comment - {comment_text}")

    zd_messages_str = "\n".join(zd_messages)
    return zd_messages_str[-3000:]

conversation = get_zd_messages()
def get_intuitPR(conversation,dictname):
    client = OpenAI()
    information = input("Provide context now:")
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
    start_idx = string.find("Warm regards,")
    if start_idx == -1:
        start_idx = string.find("Best regards,")
    if start_idx == -1:
        start_idx = string.find("Regards,")
    if start_idx == -1:
        start_idx = string.find("Sincerely,")
    if start_idx != -1:
        string = string[:start_idx]
    else:
        string = string
    dictname["intuitPR"] = string
    

products = {
    "vd": "Volt Delta (NA)",
    "exnda": "GFI - Exinda Network Orchestrator",
    "exinda": "GFI - Exinda Network Orchestrator",
    "ssmart": "StreetSmart",
    "ffm": "Field Force Manager",
    "pb": "Playbooks",
    "bonzai": "Bonzai",
    "firstrain": "Firstrain",
    "lg": "GFI - LanGuard",
    "eventsmanager": "GFI - EventsManager",
    "evmgr": "GFI - EventsManager",
    "em": "GFI - EventsManager",
    "mobilogy": "Mobilogy",
    "xinet": "Northplains Xinet",
    "kandy": "Kandy",
    "alp": "ALP",
    "kc": "Kayako Classic",
    "kayakoc": "Kayako Classic",
    "jive": "Jive",
    "jvhop": "Jive HOP",
    "jivehop": "Jive HOP",
    "kayako": "Kayako",
    "tnk": "Kayako",
    "streetsmart": "StreetSmart",
    "exnda": "Exinda Network Orchestrator",
    "kayakoclassic": "Kayako Classic",
    "kclassic": "Kayako Classic",
    "fieldforce": "Field Force Manager",
    "fieldforcemanager": "Field Force Manager",
    "evntsmgr": "GFI - EventsManager",
    "jvcld": "Jive Cloud",
    "mob": "Mobilogy Now",
    "cf": "Central Finance",
    "ans": "AnswerHub",
    "acrm": "ACRM",
    "ev": "Everest",
    "bz": "Northplains Xient",
    "sky": "Skyvera Analytics",
    "acorn": "Acorn",
    "l3" : "Learn and Earn",
    }


# Define dict with JIRA links
jira_links = {
    "vd": "https://workstation-df.atlassian.net/browse/ZTPS-30562",
    "ev": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EVNOTREAL",
    "exinda": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EXOS/issues",
    "ssmart": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues",
    "ffm": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues", #StreetSmart link for FFM
    "pb": "https://trilogy-eng.atlassian.net/jira/software/c/projects/INSIDESALES/issues", # Playbooks is INSIDESALES
    "bonzai": "https://trilogy-eng.atlassian.net/jira/software/c/projects/BONZAI/issues",
    "firstrain": "https://trilogy-eng.atlassian.net/jira/software/c/projects/FIRSTRAIN/issues",
    "lg": "https://trilogy-eng.atlassian.net/jira/software/c/projects/GFIL/issues",
    "eventsmanager": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EVENTSMGR/issues",
    "xinet": "https://trilogy-eng.atlassian.net/jira/software/c/projects/XINET/issues",
    "kandy": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KANDY/issues",
    "alp": "https://trilogy-eng.atlassian.net/jira/software/c/projects/ALP/issues",
    "kc": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KAYAKOC/issues",
    "jive": "https://trilogy-eng.atlassian.net/jira/software/c/projects/JVCLD/issues",
    "jvhop": "https://trilogy-eng.atlassian.net/jira/software/c/projects/JVHOPST/issues",
    "kayako": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KAYAKO/issues",
    "streetsmart": "https://trilogy-eng.atlassian.net/jira/software/c/projects/STREETSMART/issues",
    "mob": "https://trilogy-eng.atlassian.net/jira/software/c/projects/MOBILOGY/issues",
    "evmgr": "https://trilogy-eng.atlassian.net/jira/software/c/projects/EVENTSMGR/issues",
    "bizops": "https://workstation-df.atlassian.net/browse/IGBIZOPS/issues",
    "acorn": "https://workstation-df.atlassian.net/browse/IBUENG/issues",
    "cf": "https://workstation-df.atlassian.net/jira/core/projects/CFIN/issues",
    "ans": "https://trilogy-eng.atlassian.net/jira/software/c/projects/ANSWER/issues",
    "acrm": "https://trilogy-eng.atlassian.net/jira/software/c/projects/CRM/issues",
    "tnk": "https://trilogy-eng.atlassian.net/jira/software/c/projects/KAYAKO/issues",
    "bz": "https://workstation-df.atlassian.net/jira/core/projects/IGBIZOPS/issues",
    "sky": "no JIRA",
    "l3" : "no JIRA",
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
    "byline": "Best regards,\nMunawar Shah\n" +" Support Team\n",
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
    #Pieces of JIRA escalation
#Insert JIRA link from jira_links dict
    "jirabiz": "[Jira link]",
    "prepesc1": "**Issue Type:** Task\n",
    "prepesc2": "**Subject:** &nbsp;\n",
    "prepesc3": "**Description:** &nbsp;\n",
    "prepesc4": "**Zendesk Ticket IDs:** &nbsp;\n",
    "prepesc5": "**Attachments:** &nbsp;\n",
    "prepesc6": "**Unit Type:** &nbsp;\n",    
    "intuitPR": "",
}

#define a function to modify the final string
def modifystring(string, scenario,product):
    string = string.replace("Support Team", products[product] + " Support Team")
    string = string.replace("[Jira link]", "[Jira link](" + jira_links[product] + ")")
    string = string.replace("**External Team:** &nbsp; ", "**External Team:** &nbsp; " + scenario_ext[scenario])
    string = string.replace("**On Hold Reason:** &nbsp;", "**On Hold Reason:** &nbsp; " + scenario_reason[scenario])
    string = string.replace("**On Hold Timer:** &nbsp; &nbsp; ", "**On Hold Timer:** &nbsp; &nbsp; " + scenario_timer[scenario])
    string = string.replace("**Escalation Target:** &nbsp; &nbsp; \n", "**Escalation Target:** &nbsp; &nbsp; " + scenario_target[scenario] + "\n")
    string = string.replace("[Product]", products[product])
    return string

# Define a function to iterate over list and extract the values, then do lookup by key and print values
def pscenario(scenario,product):
    vallist = []
    for ndex in scenario:
        value = elements[ndex]
        vallist.append(value)
    return "\n".join(vallist)
    
#Find "Support Team" in finalstring1 and insert product name before it
#    finalstring2 = finalstring1.replace("Support Team", products[product] + " Support Team")
#find [Jira link] in finalstring2 and insert the value from dictionary jira_links after it in the brackets
#    finalstring = finalstring2.replace("[Jira link]", "[Jira link](" + jira_links[product] + ")")
#    print(finalstring)
#    pyperclip.copy(finalstring)

   
# Define the scenarios using only the elements defined above

sbasic = ["instlink","action", "divider", "context"]
sbpre = sbasic[:2]
scntxt = sbasic[2:]
spr = ["pr", "intuitPR", "byline"]
sdvdr = ["divider"]
gpt = ["divider", "gpt", "gptyes"]
meta = ["mxteam", "mhreason", "mhtimer", "mhtarget"]
jira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4", "prepesc5", "prepesc6"]
cjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc6", "prepesc4", "prepesc5"]
sjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4"]
sc = ["sc1", "sc2","sc3","sc4"]

scenarios = {
    "basic": sbasic,
    "tsk": sbpre + ["l1op"] + scntxt + ["blurbtask"],
    "cst": sbpre + ["custop"] + sdvdr + spr + gpt + scntxt+ ["ret"],
    "ex": sbpre + ["extop"] + sdvdr + spr + meta + sc + scntxt+ ["ret"],
    "exsaas": sbpre + ["extop"] + sdvdr + spr + meta + sjira + scntxt+ ["ret"],
    "exold": sbpre + ["extop"] + sdvdr + spr + meta + scntxt+ ["ret"], 
    "exn": sbpre + ["extop"] + meta + scntxt + ["ret"]+ ["ret"],
    "exb": sbpre + ["extop"] + ["buop"] + sdvdr + spr + meta + ["e2b"] + scntxt + ["blurbbu"]+ ["ret"],
    "excf": sbpre + ["extop"] + sdvdr + spr + meta + cjira + scntxt+ ["ret"],
    "exbn": sbpre + ["extop"] + ["buop"] + scntxt + ["blurbbu", "e2b"],
    "exbz": sbpre + ["extop"] + sdvdr + spr + meta + jira + scntxt+ ["ret"],
    "l2": sbpre + ["l2op"] + sdvdr + spr + scntxt+ ["ret"],
    "l2n": sbpre + ["l2op"] + scntxt + ["ret"],
    "l1n": sbpre + ["l1op"] + scntxt + ["ret"],
    "clst": sbpre + ["clstop"] + sdvdr + spr + scntxt + ["ret"],
    "clsth" : sbpre + ["clstop"] + sdvdr + spr,
    "clstn": sbpre + ["clstop"] + scntxt + ["ret"],
    "clsch": sbpre + ["clscop"],
    }

scenarios_requiring_pr = ["cst", "ex", "exsaas", "exold", "exb", "excf", "exbz","l2", "clst", "clsth"]

#Define the external team with scenarios
scenario_ext = {"ex":"Internal", 
                "exsaas":"Saas Ops",
                "exn":"Central Finance",
                "exold":"BU Customer Success/Sales/SOP",
                "exbz":"BU Customer Success/Sales/SOP",
                "exb":"BU Other",
                "excf":"Central Finance",
                "basic": "",
                "tsk": "",
                "cst": "",
                "l2": "",
                "l2n": "",
                "l1n": "",
                "clst": "",
                "clsth": "",
                "clstn": "",
                "clsch": "",
                "exbn": "BU Customer Success/Sales/SOP"}

scenario_reason = {"ex":"SC",
                "exsaas":"SaaS Ops JIRA linked",
                "exn":"CFIN JIRA",
                "exold":"CFIN JIRA",
                "exbz":"BU JIRA",
                "exb":"Awaiting elevation",
                "excf":"CFIN JIRA",
                "basic": "",
                "tsk": "",
                "cst": "",
                "l2": "",
                "l2n": "",
                "l1n": "",
                "clst": "",
                "clsth": "",
                "clstn": "",
                "clsch": "",
                "exbn": "Awaiting elevation"}


scenario_timer = {"ex":"48",
                "exsaas":"9999",
                "exn":"9999",
                "exold":"9999",
                "exbz":"168",
                "exb":"4",
                "excf":"9999",
                "basic": "",
                "tsk": "",
                "cst": "",
                "l2": "",
                "l2n": "",
                "l1n": "",
                "clst": "",
                "clsth": "",
                "clstn": "",
                "clsch": "",
                "exbn": "4"}


scenario_target = {"ex":"Other",
                "exsaas":"Other",
                "exn":"Central Finance",
                "exold":"Central Finance",
                "exbz":"BU Customer Success/Sales/SOP",
                "exb":"BU Other",
                "excf":"Central Finance",
                "basic": "",
                "tsk": "",
                "cst": "",
                "l2": "",
                "l2n": "",
                "l1n": "",
                "clst": "",
                "clsth": "",
                "clstn": "",
                "clsch": "",
                "exbn": ""}

#Let user choose scenario and repeat in a while loop until quit is entered

def main():
    for name in scenarios:
        print(name)
    chosen_scenario = input()
    if chosen_scenario == "quit": 
        print("Goodbye!")
        sys.exit()
    elif chosen_scenario in scenarios:
        product = input("Product:")
        if chosen_scenario in scenarios_requiring_pr:
            conversation = get_zd_messages()
            get_intuitPR(conversation,elements)
        finalstring = pscenario(scenarios[chosen_scenario],product)
        finalstring = modifystring(finalstring,chosen_scenario,product)
        print(finalstring)
        pyperclip.copy(finalstring)

    else:
        print("Scenario is not defined")


#Check all scenarios use valid elements and warn if not

for scenario, element_seq in scenarios.items():
    for elmnt in element_seq:
        if elmnt not in elements:
            print(f"Warning: Element '{elmnt}' in scenario '{scenario}' is not defined!")

main()

