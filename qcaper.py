from bs4 import BeautifulSoup
from bs4.element import NavigableString
import pyperclip

messages = []

def preserve_newlines(tag):
    text_parts = []
    for element in tag.descendants:
        if element.parent.name == 'a':
            continue
        if isinstance(element, NavigableString):
            text = str(element).replace('\n', '[newline]')
            text_parts.append(text)
        elif element.name == 'br':
            text_parts.append('[newline]')
        elif element.name == 'a':
            text_parts.append(str(element))
    return ''.join(text_parts).replace('[newline]', '\n')

def replace_substring(original_string, start_index, end_index, replacement_string):
    """
    Replace a substring within `original_string` that starts at `start_index` and ends at `end_index`
    with `replacement_string`.
    
    :param original_string: The string to modify.
    :param start_index: The start index of the substring to replace.
    :param end_index: The end index of the substring to replace.
    :param replacement_string: The string to insert in place of the removed substring.
    :return: The modified string with the replacement.
    """
    if start_index < 0 or end_index > len(original_string):
        return original_string  # Index out of bounds, return original string.
    
    # Get the parts before and after the substring to replace
    first_part = original_string[:start_index]
    last_part = original_string[end_index:]

    # Return the concatenation of the first part, the replacement string, and the last part
    return first_part + replacement_string + last_part


# Get HTML content from clipboard and pass it to var soup
html_content = pyperclip.paste()
soup = BeautifulSoup(html_content, 'html.parser')
divs = soup.find_all('div', {'class': ['zd-comment']})
if divs:
    last_div = divs[-1] 
else:
    last_div = None
if last_div is None:
    print("No div")
else:
    comment_text=preserve_newlines(last_div)
    print(comment_text)
start_idx = comment_text.find('Dear')
# if not found try again
if start_idx == -1:
    start_idx = comment_text.find('Hi')
# if still not found try again
if start_idx == -1:
    start_idx = comment_text.find('Hello')

# Find the last occurrence of the string "team"
end_idx = comment_text.rfind('Support Team')
if end_idx == -1:
    end_idx = comment_text.rfind('egards')

# Check if both strings are found
if start_idx != -1 and end_idx != -1:
    # Slice the string to keep only the desired portion
    # Note: end_idx is adjusted to exclude the word "team"
    comment_text = comment_text[start_idx:end_idx+12]
else:
    print("One or both of the target strings were not found.")
    print(comment_text)

# Replace the substring
start_idx2 = comment_text.find('egards,')+8
end_idx2 = comment_text.rfind('\n')
if start_idx2 != -1 and end_idx2 != -1:
    comment_text = replace_substring(comment_text, start_idx2, end_idx2, "Munawar Shah")
    messages.append(f"{comment_text}")

else:
    print("One or both of the target strings were not found at the end.")
    print(comment_text)

# Ex#print(str(soup.prettify())[:500])
#for div in divs:
#    if div is None:
#        print("No div") 
#    else:
#    # Get the Name
#        sender_name = "No name"
#        for title in div.find_all_previous('div', {'class': ['sc-1gwyeaa-2 icjiLH','sc-yhpsva-1 dtIjfP']}):
#            strong_text = title.find('strong')
#            if strong_text:
#                sender_name = strong_text.text
#                break
    # Get the Comment      
#        comment_div = div[-1]
#        comment_text = "No comment"
#        if comment_div is not None:
#            comment_text = comment_div.text
#        

conversation = '\n'.join(messages)
print(conversation)
pr= conversation
## Copy to clipboard
pyperclip.copy(pr)
