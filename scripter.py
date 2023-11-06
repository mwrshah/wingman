##A scripting tool
# Import the pyperclip module.
import pyperclip
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
    "sc1": "**SC:**&nbsp;",
    "sc2": "**Subject:**&nbsp;",
    "sc3": "**Description:**&nbsp;\n",
    
    "sc4": "**Attachments:**&nbsp; \n",
    #Pieces of JIRA escalation
#Insert JIRA link from jira_links dict
    "jirabiz": "[Jira link]",
    "prepesc1": "**Issue Type:** Task\n",
    "prepesc2": "**Subject:** &nbsp;\n",
    "prepesc3": "**Description:** &nbsp;\n",
    "prepesc4": "**Zendesk Ticket IDs:** &nbsp;\n",
    "prepesc5": "**Attachments:** &nbsp;\n",
    "prepesc6": "**Unit Type:** &nbsp;\n",    
}

#define a function to modify the final string
def modifystring(string, scenario):
    string.replace("Support Team", products[product] + " Support Team")
    string.replace("[Jira link]", "[Jira link](" + jira_links[product] + ")")
    string.replace("**External Team:** &nbsp; ", "**External Team:** &nbsp; " + scenario_ext[scenario])
    return string



#define a function to iterate over the items in lists basic for example and print to a separate line

def printl(list):
    for item in list:
        print(item)
def printd(dict):
    for key, value in dict.items():
        print(key, value)
# Define a function to iterate over list and extract the values, then do lookup by key and print values
def pscenario(scenario,product):
    vallist = []
    for ndex in scenario:
        value = elements[ndex]

#Add value to a list, and then make a string with the join method with "\n" as the separator
        vallist.append(value)
    finalstring1 = "\n".join(vallist)
#Find "Support Team" in finalstring1 and insert product name before it
    finalstring2 = finalstring1.replace("Support Team", products[product] + " Support Team")
#find [Jira link] in finalstring2 and insert the value from dictionary jira_links after it in the brackets
    finalstring = finalstring2.replace("[Jira link]", "[Jira link](" + jira_links[product] + ")")
    print(finalstring)
    pyperclip.copy(finalstring)

   
# Define the scenarios using only the elements defined above

sbasic = ["instlink","action", "divider", "context"]
sbpre = sbasic[:2]
scntxt = sbasic[2:]
spr = ["pr", "byline"]
sdvdr = ["divider"]
gpt = ["ret", "gpt", "gptyes"]
meta = ["mxteam", "mhreason", "mhtimer", "mhtarget"]
jira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4", "prepesc5", "prepesc6"]
cjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc6", "prepesc4", "prepesc5"]
sjira = ["jirabiz", "prepesc1", "prepesc2", "prepesc3", "prepesc4"]
sc = ["sc1", "sc2","sc3","sc4"]

scenarios = {
    "basic": sbasic,
    "tsk": sbpre + ["l1op"] + scntxt + ["blurbtask"],
    "cst": sbpre + ["custop"] + sdvdr + spr + scntxt+ ["ret"],
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

#Define the external team with scenarios
scenario_ext = {"ex":"Internal", 
                "exsaas":"Saas Ops",
                "exn":"Central Finance",
                "exold":"BU Customer Success/Sales/SOP",
                "exbz":"BU Customer Success/Sales/SOP",
                "exb":"BU Other",
                "excf":"Central Finance"}

#Let user choose scenario and repeat in a while loop until quit is entered

while True:
    for name in scenarios:
        print(name)
    chosen_scenario = input()

#Ask user for product only if the last letter of the chosen scenario is not n
#    if chosen_scenario[-1] != "n":
#        print("Product:")
#        product = input()

#    for prod in Prod_list: 
#        print(prod)
#    product = input()
    if chosen_scenario == "quit":
        print("Goodbye!")
        break
    elif chosen_scenario in scenarios:
        product = input()
        pscenario(scenarios[chosen_scenario],product)

    else:
        print("Scenario is not defined")


#Check all scenarios use valid elements and warn if not

for scenario, element_seq in scenarios.items():
    for elmnt in element_seq:
        if elmnt not in elements:
            print(f"Warning: Element '{elmnt}' in scenario '{scenario}' is not defined!")



##OLD Ask user for input
##make the program run unit the user enters scenario "qt"
#chosen_scenario = ""
#print("Pick one:")
#
#for name in scenarios:
#    print(name)
#
#chosen_scenario = input()
#    
#Ask user for product only if the last letter of the chosen scenario is not n
#if chosen_scenario[-1] != "n":
#    print("Product:")
#    product = input()
#
#
#if chosen_scenario in scenarios:
#    output = "\n".join([elements[element] for element in scenarios[chosen_scenario]])
#    print(output)
#    pyperclip.copy(output)
#else:
#    print("scenario is not defined")
