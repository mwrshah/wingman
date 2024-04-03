#SUBBED only for clarity
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from printing_funk import *

    #Find the path where the script is running 
    # to default to config bundled with the executable
def get_resource_path():
    try:
        base_path = sys._MEIPASS
    except Exception:
        print("Error: Could not find the resource path in sys._MEIPASS.")
        base_path = os.path.dirname(os.path.abspath(__file__))
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

def get_first_pr(soup):
        #Vars for ZD scraping
    class_chat = 'sc-wv3hte-1 epkhmy'
    class_chat2 = 'sc-wv3hte-0 eKImJ'
    class_AI_integration = "sc-5rafq2-0 sc-7uf44v-0 gXPtvy"
    pr_classes = ['sc-5rafq2-0 gEMoXX',class_chat,class_chat2,class_AI_integration, "sc-11lm90w-0 dehgfD","sc-54nfmn-2 bLEhML","sc-54nfmn-1 eksNum","sc-54nfmn-2 jqMmnW"]
        #BEGIN
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

def get_zd_messages(soup,f_pr):  
        #Name finder
    #Takes a div and returns the name of the sender, and appends it to a unique list
    def name_finder(div):
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
            names["support"] = names["support"] + [sender_name]
        if numtal in messagecounter:
            index = messagecounter.index(numtal)+1

        #Vars for ZD scraping
    class_chat = 'sc-wv3hte-1 epkhmy'
    class_chat2 = 'sc-wv3hte-0 eKImJ'
    class_AI_integration = "sc-5rafq2-0 sc-7uf44v-0 gXPtvy"
    pr_classes = ['sc-5rafq2-0 gEMoXX',class_chat,class_chat2,class_AI_integration, "sc-11lm90w-0 dehgfD","sc-54nfmn-2 bLEhML","sc-54nfmn-1 eksNum","sc-54nfmn-2 jqMmnW"]
    
        #BEGIN
    zd_messages = []
    messagecounter = []
    names = {"requester": [],
             "support": [],}
    collection = []
    collect_first = [] 
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
        subj_print = " Subject: " +  subj
    else:
        subj_print = ""
    print_bright(subj_print,yellowf)

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
                names["requester"] = [sender_name]
            
            collect_first = [sender_name,first_commentorIN]
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
    zd_in_list = ['sc-54nfmn-1 cfDlbe']
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
                names["support"] = names["support"] + [sender_name]
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
                if len(split_fed_print_list) > 0:
                    if split_fed_print_list[0] == "":
                        split_fed_print_list.pop(0)
                    if len(split_fed_print_list) > 0:
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
                collection.append([sender_name,comment_text_pre])
                zd_messages.append(f"{sender_name} said: \n | {comment_text}")

        #Separately putting out ZD Messages as a list
    zd_messages_str = "\n".join(zd_messages)
    if first_commentorIN[:50] == f_pr[:50] and len(zd_messages_str) > 100:
        zd_messages_str =  zd_messages_str[-7000:]
    elif collect_first:
        collection.insert(0, collect_first)
        zd_messages_str =  first_IN + "\n" + zd_messages_str[-7000:]
    if subj != "": 
        collection.insert(0,["Subject",subj])
    list_of_messages = [["",""]]
    
    if collection != []:
        list_of_messages = collection.copy() 

    found_colon = zd_messages_str.find(":")
    if found_colon != -1:
        zd_messages_str = zd_messages_str[:found_colon+1] + "\n" + subj + "\n" + zd_messages_str[found_colon+1:]
   # with open(f"{dir_path}/logs/log_last_zd_messages.txt", "w") as f:
   #     f.write("ZD MESSAGES including FIRST IN: \n\n" + zd_messages_str)
   # with open(f"{dir_path}/logs/log_last_zd_messages.txt", "a") as f:
   #     f.write("\n\n\n\n\n\nfirst_IN FOUND: \n" + first_IN)

    return zd_messages_str, list_of_messages, names

