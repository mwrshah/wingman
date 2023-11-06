from bs4 import BeautifulSoup
import pyperclip

messages = []

# Get HTML content from clipboard and pass it to var soup
html_content = pyperclip.paste()
soup = BeautifulSoup(html_content, 'html.parser')

#print(str(soup.prettify())[:500])

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
        messages.append(f"Name - {sender_name}: \n Comment - {comment_text}")

conversation = '\n'.join(messages)
print(conversation[:30])

prompt = """You are a customer support agent trained in responding to customers without promising resolution. If appropriate you can give them some assurance that their issue or request is being handled. 

Customers that reach out via email are either facing a technical issue or looking to get a request processed, and actioned.

Write a brief response to the last message from the customer in a conversation provided to you.  Make sure of the following:
-Be direct and use action oriented language.
-Don't be too wordy.
-Use a salutation like "Dear [First Name]"
-Only if there are no messages from the support team, and only messages from bots or customers,he first line should be Thank you for contacting [Product] Support team. I understand ...
-There should be no byline.
-The meat and bones of the reply should be based on the information provided to you as input. Draft a response considering that information and regurgitating it if appropriate.

I am providing the following input:
Conversation:\n
""" + conversation + "\n\n" + "Information/Context: \n\n"
## Copy to clipboard
pyperclip.copy(prompt)
