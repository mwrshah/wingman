from bs4 import BeautifulSoup
from bs4.element import NavigableString
import pyperclip
import sys

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

def replace_substring(original_string, regards_index,  replacement_string, newline_index):
    """
    Replace a substring within `original_string` that starts at `start_index` and ends at `end_index`
    with `replacement_string`.
    
    :param original_string: The string to modify.
    :param start_index: The start index of the substring to replace.
    :param end_index: The end index of the substring to replace.
    :param replacement_string: The string to insert in place of the removed substring.
    :return: The modified string with the replacement.
    """
    if regards_index < 0 or newline_index > len(original_string):
        return original_string  # Index out of bounds, return original string.
    
    first_part = original_string[:regards_index]
    last_part = original_string[newline_index:]

    # Return the concatenation of the first part, the replacement string, and the last part
    return first_part + '\n' + replacement_string + last_part


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


# Finding Dear
foundone = False
openings = ['Dear','Hi','Hello']
for opening in openings:
    dear_idx = comment_text.find(opening)
    if dear_idx != -1:
        foundone = True
        break
print(dear_idx)


closings_full = ['Support Team', 'egards,','Thanks','Thank','hank']
last_thanks = comment_text.rfind('egards')
if last_thanks == -1:
    last_thanks = comment_text.rfind('hank')

# Finding Support Team
foundsecond = False
for closing in closings_full:
    end_idx = comment_text.rfind(closing)
    count = comment_text.count(closing)
    print(closing, ":" ,count)
    if end_idx != -1 and count < 2 and end_idx > 150 and end_idx > last_thanks:
        foundsecond = True
        break
print(f"found second on first attempt {foundsecond}")

def slicefinder(text, exclude_first, list_of_strings):
    for string in list_of_strings:
        spliced_text = text[exclude_first:]
        if spliced_text:
            count = spliced_text.count(string)
            idx = spliced_text.rfind(string)
            if idx != -1:
                idx += exclude_first
            if count > 1:
                return -1, False
            elif idx > 150 and idx > last_thanks:
                idx = spliced_text.rfind(string) + exclude_first
                if idx != -1 and idx > exclude_first:
                    return idx, True
            else:
                return -1, False

if not foundsecond:
    end_idx, foundsecond = slicefinder(comment_text, 200, closings_full)
if not foundsecond:
    end_idx, foundsecond = slicefinder(comment_text, 300, closings_full)
if not foundsecond:
    end_idx, foundsecond = slicefinder(comment_text, 400, closings_full)

#print(f"found second on all attempts: {foundsecond}")  
# Check if both strings are found


if dear_idx != -1 and end_idx != -1:
    comment_text = comment_text[dear_idx:end_idx+12] #Functional slice for next steps
elif dear_idx != -1:
    comment_text = comment_text[dear_idx:]
else: 
    print("One or both of the target strings were not found.")
    sys.exit()
# Finding Regards
#Inserting my name in
closings = ['egards,','Thanks','Thank','hank']

found = False
for closing in closings:
    regards_idx = comment_text.rfind(closing)
    if regards_idx != -1 and regards_idx > 100:
        regards_idx += len(closing)
        found = True
        break
    if not found:
        regards_idx = len(comment_text[:-10])

print(f"found regards: {found}")
newline_idx = comment_text.rfind('\n')
if newline_idx < regards_idx and newline_idx != -1:
    newline_idx = comment_text.find('\n', regards_idx)
    print("Had to fire forward search")
if newline_idx == -1:
    newline_idx = regards_idx + 1
    print("Had to go to last resort")

print(comment_text)
if regards_idx != -1 and newline_idx != -1:
    comment_text = replace_substring(comment_text, regards_idx,  "Munawar Shah", newline_idx)
    print("AFTER\n"*5, comment_text)
else:
    print("One or both of the target strings were not found at the end.")

pr = comment_text
#pr = '\n'.join(messages)
print("Copied to clipboard")
pyperclip.copy(pr)
