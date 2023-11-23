
import sys

def scenario_extractor(input_string):
    
    all_scenarios = ["tsk", "cst", 
                     "ex", "exsaas", "exold", 
                     "exn", "exb", "excf", "exbn", 
                     "exbz", "l2", "l2n", "l1n", 
                     "clst", "clsth", "clstn", "clsch"
                     "qc","sum"]
       #Define subsets
    scenario_subsets= {
            "bu":["exb","exbn"], #Moved up for specificity of exbz case otherwise that gets wiped
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
            "chat":["clsch"],
            "clst":["clst","clstn"],
            "saas":["exsaas"],
            "in_esc_update": ["exold"],
    }
    def pbug(name,value):
        print("Printing "+name+ ": "+value+"\n")

    parse_string = input_string.lower().strip()
    parse_string = parse_string[:50]
    
    #pbug("parse_string",parse_string)
    
    gt_idx1 = parse_string.find(">")
    dot_idx1 = parse_string.find(".")
    
    #if both found
    if gt_idx1 != -1 and dot_idx1 != -1:
        if gt_idx1 < dot_idx1:
            gt_first = True
        else:
              gt_first = False
    else:
        gt_first = True #Possibly
    
    #if > found and first fine, otherwise prefer first
    if gt_idx1 != -1 and gt_first:
        end_idx1 = parse_string.find(">")

    elif dot_idx1 != -1:
        end_idx1 = parse_string.find(".")
    
    else:
        end_idx1 = parse_string.find(".")
        

    #pbug("dot_idx1",str(dot_idx1)) 
    #pbug("gt_idx1",str(gt_idx1))
    
    second_parse_string = parse_string[end_idx1+1:]
    
    end_idx2 = None
    if gt_idx1 != -1:
        end_idx2 = second_parse_string.find(">") + end_idx1+1
    elif dot_idx1 != -1 and end_idx2 == None:
         end_idx2 = second_parse_string.find(".") + end_idx1+1
    else: 
        end_idx2 = end_idx1 + 24 #24 is a random number. 
        
#end_idx1 will never be unassigned when end_idx2 is called upon because if it is then the following block applies.

    if end_idx1 == -1:
        slice1 = parse_string[:40]
        slice1 = " " + slice1 + " " #some of the search terms are defined with leading spaces so this is necessary for search term starting at the beginning of the sentence. The benefit of having space in the search term is it won't fire for term appearing within a word. Example " sc ". 

        slice1 = slice1.replace(".", " .")
        slice2 = " " + parse_string + " "
        slice3 = parse_string + " "
    
    else:
        slice1 = parse_string[:end_idx1]
        slice1 = " " + slice1 + " "
        slice1 = slice1.replace(".", " .")
        slice2 = parse_string[end_idx1+1:end_idx2]
        slice2 = " " + slice2 + " "
        slice2 = slice2.replace(".", " .")
        slice3 = parse_string[end_idx2+1:]    

    pbug("slice1",slice1)
    pbug("slice2",slice2)
    pbug("slice3",slice3)

    def negation_check(string):
        negations = ["don't", "not", "n't"]
        if any(string[-7:].find(word) != -1 for word in negations):
            return True
        else:
            return False

    intentlist = [] #COLLECTION OF ALL INTENTS FOUND
    lookuplist = []
    
    intent_sets = {
        "bu" : ["business unit", " bu ", "exb", "exbn", "noc ",], #Moved up to retain specificly the exbz case in the set intersection
        "cls" : ["close", "cls"],
        "cst" : ["customer", "cust", "cst"],
        "l1" : ["l1", "level 1", "level one", "l1n"],
        "l2" : ["l2", "level 2", "level two", "l2n"],
        "esc" : ["external", "escalate", "elevate", " ext ", "send this to","send it to", "send to"],
        "yes_pr" : ["a pr ","write", "draft", "compose", "yes pr"],
        "no_pr" : ["no pr", "don't write", "no reply", "no response", "don't draft","don't draft"],
        "qc" : ["quality", " qc ","check", " chk ", "chck", " qlt",  "review",],
        "task" : ["task", "tsk"],
        "sum" : ["summarize", "summary", " sumr "," sumz ", " smz ", " smry ", " sm "],
        "cf" : ["to finance"," the finan", " fin ","cf ", "central finance", "treasury", " ap ", "collect cash", "udf", "accounts pay", " rishap", "cquery", "write off", "vendor reg", "vendor pay", "o2c", "record maint", "record mn", "record man", "record mg"],
        "sc" : [" sc ","side conv", "side conversation", " ex ",],
        "bz" : ["bu jira", "business ops", " bz ", "bizops", "exbz"," account m","ount mng", " ount mg"],
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

    #intent extractor collects the first intent and adds the overall set name to the intentlist
    def intent_extractor(string, intent_sets_dict):
        if not string:
            return None
        for searchtermlist in intent_sets_dict.values():
            for intent in searchtermlist: 
                pbug("intent checked ",intent)
                where_is_it = string.find(intent) 
                if where_is_it != -1: 
                    new_string = string[:where_is_it]
                    #pbug("new_string",new_string)
                    if not negation_check(new_string):
                        for key, value in intent_sets_dict.items():
                            if intent in value:
                                #pbug("intent",intent)
                                #pbug("key",key)
                                found_intent = key
                                intentlist.append(found_intent)
        return None
    
    intent_extractor(slice1,intent_sets) 
    intent_extractor(slice2,intent_sets)
    pbug("intentlist",str(intentlist)) #DEBUG 

    tempintentionsets = []
    if not intentlist:
        print("No intent found"*20)
    for intent in intentlist:
        intent_set = set(scenario_subsets[intent])
        tempintentionsets.append(intent_set)
    #pbug("tempintentionsets",str(tempintentionsets))
    
    if tempintentionsets: 
        intersectionset = tempintentionsets[0]
        #pbug("intersectionset",str(intersectionset))
    else:
        intersectionset = set()
    for current_set in tempintentionsets[1:]:
        intersectionset &= current_set
    
    lookuplist = list(intersectionset)
    pbug("lookuplist",str(lookuplist))
    Flowbreak1 = "You need to tell Wingman what you intend to do AND give a clue e.g. Escalate to BU no PR. We need approval from account management to proceed"
    Flowbreak2 = "Wingman is confused about what you want to do.\n Try being more specific"
    
    if len(lookuplist) == 0:
        print(Flowbreak1)     
    elif len(lookuplist) > 1:
        lookuplist = [scenario for scenario in lookuplist if not scenario.endswith("n")]
        print(Flowbreak2)
    if len(lookuplist) > 1:
        return 
    elif len(lookuplist) == 1:
        return lookuplist[0]

while True:
    user_input = input("Enter your text: ")
    if user_input == "exit":
        sys.exit()
    else:
        scenario = scenario_extractor(user_input)
        print("Scenario: "+str(scenario))
