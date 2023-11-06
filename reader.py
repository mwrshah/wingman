import os
import json

#Define a function to look for all json files in a directory and return a list of files, then ask user to select, and then load json to dictionary, and print the result

#Define a function to print the key value pair in a dictionary
def separator():
    print("............")
    print("............")
    print("............")
    print("............")

#Define a function to print all the key value pairs in a dictionary with an additional number as index
def print_pair(dictionary):
    lstitems = []
    for key, value in dictionary.items():
        lstitems.append(str(key)+": "+str(value))
    for i in range(len(lstitems)):
        print(str(i+1) + " - " + lstitems[i])

def load_json():
    #look for json files in the current directory
    json_files = [pos_json for pos_json in os.listdir(os.getcwd()) if pos_json.endswith('.json')]
    #print the list of json files
    separator()
    print("The following json files are available:")
    for i in range(len(json_files)):
        print(str(i+1) + ": " + json_files[i])
    #ask user to select a json file or quit to exit
    file_index = input("Select file to load OR 'quit' OR 'delmode': ")
    #if user types quit, exit the program
    if file_index == "quit":
        exit()
    #If user types delmode, delete a key value pair
    elif file_index == "delmode":
        delete_pair(json_data)
    #if user types a number, load the json file or if not valid then error "Enter a valid number"
    elif not file_index.isdigit():
        print("Enter a valid number")
    #if user types a number that is not in the list, error "Enter a valid number"
    elif int(file_index) > len(json_files):
        print("Enter a valid number")
    else:
        #load json file to dictionary
        file_index_corrected = int(file_index) - 1
        with open(json_files[int(file_index_corrected)]) as json_file:
            json_data = json.load(json_file)
        #print the result
        print_pair(json_data) 

#Define a function to delete a key value pair in a dictionary after taking user input about the index number to delete
def delete_pair(dictionary):
    #print all the key value pairs in the dictionary with an additional number as index
    print_pair(dictionary)
    #ask user to select a number to delete
    delete_index = input("Please select a number to delete: ")
    #if user types a number, delete the key value pair or if not valid then error "Enter a valid number"
    if not delete_index.isdigit():
        print("Enter a valid number")
    #if user types a number that is not in the list, error "Enter a valid number"
    elif int(delete_index) > len(dictionary):
        print("Enter a valid number")
    else:
        #delete the key value pair
        delete_index_corrected = int(delete_index) - 1
        del dictionary[list(dictionary)[int(delete_index_corrected)]]
        #print the result
        print_pair(dictionary)

#Define a function 
def main():
    while True:
        load_json()
main()
