import json
import os

# Define a function to load a dictionary from a json file with a name as parameter giving the dictionary the same name. If the json doesn't exist create one and ask for a name.

def save_dict(name, dictionary):
    with open(name + ".json", "w") as f:
        json.dump(dictionary, f)

def load_dict(name):
    try:
        with open(name + ".json", "r") as f:
            return json.load(f)
        return {}
#Define an except clause for FileNotFoundError and create a new json file with the name given by the user
    except FileNotFoundError:
        print("File not found, creating a new file")
        with open(name + ".json", "w") as f:
            json.dump({}, f)
        return {}

#Define a function to ask user for input "What do you want to teach Scripter?", the dictionary is the name of the json file to load using load_dict to a dictionary, then ask for key, value pairs for input, until user enters "quit", When the user enters "quit" save to file using save_dict

def teach_scripter(name):
    dictionary = load_dict(name)
    print ("Reverting to single entry")
    while True:
        print("Enter the key")
        key = input()
        if key == "quit":
            break
        print("Enter the value")
        value = input()
        dictionary[key] = value
        save_dict(name, dictionary)

# Define a function like teach_scripter() but instead of key value pairs it should support batch enter as "key = value, key1 = value1". Break if data is not in the same format

def teach_scripter_batch(name):
    dictionary = load_dict(name)
    while True:
        print("Load the data as key = value separated by commas, quit, or fallback to single entry")
        d = input()
        if d == "quit":
            exit()
        try:
            pairs = d.split(",")
            for pair in pairs:
                #find inverted commas and replace with nothing
                pair = pair.replace('"', "")
                key, value = pair.split("=")
                #strip out inverted commas and spaces from key and value and enter into dictionary
                dictionary[key.strip()] = value.strip()
                save_dict(name, dictionary)
                print("Saved")
        except:
            print("Invalid data, reverting to single entry")
            break
def main(): 
    print("Welcome to Scripter Trainer")
    print("Broadly in what category do you want to teach Scripter?Or else 'quit'")
    #search for json files and print a list
    files = os.listdir()
    for file in files:
        if file.endswith(".json"):
    #print the filename after stripping .json from the end
            print(file[:-5])
    name = input()
    if name == "quit":
        exit()
    print("-------------------Start of existing data----------------")
    currentdict = load_dict(name)
    for key, value in currentdict.items(): 
        print(key,":", value)
    teach_scripter_batch(name)
    teach_scripter(name)

main()
