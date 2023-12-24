#SUBBED FOR clarity
import os
import shutil
import textwrap
import platform

    #Vars for printing
terminal_width = shutil.get_terminal_size().columns
chrt = "|" #· ⋮
subindent = " "+chrt+" "
available_width = terminal_width - len(subindent)
    #Colors
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


def print_bright(message, color_code):
    print(f"{color_code}{message}{resetf}")

def term_print_string(string,indent):
        wrapped_out = []
        string = string.replace("\n","}n")
        stringlist = string.split("}n")
        for sliver in stringlist:
            wrapped_sliver = textwrap.fill(sliver, width = terminal_width-len(indent), 
                                           initial_indent = indent, 
                                           subsequent_indent = indent)
            wrapped_sliver = wrapped_sliver.replace("}n","\n")
            wrapped_out.append(wrapped_sliver)
        string_out = "\n".join(wrapped_out)
        return string_out

def print_wrapped(string,color):
     wrapped_string = textwrap.fill(string, width = terminal_width-4, initial_indent = "    ", subsequent_indent = "    ")
     print_bright(wrapped_string,color)

def print_logo():
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

    print_bright(textwrap.fill("Wingman v0.7beta",
                               terminal_width-10)
                                .rjust(terminal_width-4),whitef)
def clear_terminal():
    if platform.system() == "Windows":
        os.system('cls')  
    else:
        os.system("clear && printf '\033[3J'")  

def set_terminal_size(rows, columns):
    if platform.system() == "Windows":
        os.system(f'mode con: cols={columns} lines={rows}')

set_terminal_size(30, 100)


def bylinestripper(string):
    start_idx = string.find("Warm regards,")
    if start_idx == -1:
        start_idx = string.find("Best regards")
    if start_idx == -1:
        start_idx = string.find("Best Regards")
    if start_idx == -1:
        start_idx = string.find("Regards")
    if start_idx == -1:
        start_idx = string.find("Sincerely,")
    if start_idx == -1:
        start_idx = string.find("Kind regards,")
    if start_idx == -1:
        start_idx = string.find("Thanks,")
    if start_idx == -1:
        start_idx = string.find("Best regard,")
    if start_idx == -1:
        start_idx = string.find("Best,")
    if start_idx != -1:
        return string[:start_idx-1] #Also removes message history after byline
    else:
        return string

