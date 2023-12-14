import difflib

#to use, put both files along with this script in a new folder
#append comp to the beginning of the file names
#run this script

with open ('comp_wingman.py', 'r') as f_toedit:
    f_toedit_text = f_toedit.readlines()

with open ('comp_wingman_win_source.py', 'r') as f_source:
    f_source_text = f_source.readlines()

diff = difflib.unified_diff(f_toedit_text, f_source_text, fromfile='comp_wingman.py', tofile='comp_wingman_win_source.py', lineterm='')
for line in diff:
    print(line)



