#!/usr/bin/env python
import sys, re, os 
import subprocess
import json

# prompt
def print_usage():
    print("usage: notes [--add | --remove <path-to-directory>]")
    print("       notes [key]")

# return absolute path of the given directory
def get_absolute_path(directory):
    root = os.getcwd()
    if root[0] == '/':
        return directory 
    else:
        return root + "/" + directory 

def search_file(L, dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".md"):
                L.append(os.path.join(root, file).replace(dir, '', 1))
    
def notes_add_dir(cfg_filepath, add_directory):
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            config = json.load(f)
        if add_directory in config:
            print(add_directory + " exists!")
        elif not os.path.exists(add_directory):
            print("No such directory!")
        else:
            with open(cfg_filepath, "w") as f:
                config[add_directory] = []
                search_file(config[add_directory], add_directory)
                json.dump(config, f)
    else:
        with open(cfg_filepath, "w") as f:
            config = {add_directory:[]}
            search_file(config[add_directory], add_directory)
            json.dump(config, f)

def notes_remove_dir(cfg_filepath, remove_dir):
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            config = json.load(f)
        if remove_dir not in config:
            print("Not added!")
        else:
            with open(cfg_filepath, "w") as f:
                del config[remove_dir]
                json.dump(config, f)
    else:
        print("Not Configured!")

def cmp_similar(cfg_filepath, pattern):
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            candi = []
            config = json.load(f) 
            for dir in config.keys():
                for file in config[dir]:
                    if pattern.search(file.split('.')[-2]):
                        if not os.path.exists(dir + file):
                            print('File corruption')
                            print('Please check ' + dir)
                            exit()
                        else:
                            candi.append(dir + '/' + file)
            if len(candi) == 1:
                subprocess.call('vim ' + candi[0], shell = True)
            elif len(candi) > 1:
                print("There are some files you may want to access:")
                for iterm in candi:
                    print(iterm)
            else: print("Not find!")
    else:
        print("Not Configured!")


if __name__ == "__main__":
    args = sys.argv[1:]
    cfg_filepath = os.path.expanduser('~') + '/'+ ".notes_config"
    if len(args) == 2:
        directory = args[1]
        directory = get_absolute_path(directory)
        if args[0] == '-a' or args[0] == '--add':
            notes_add_dir(cfg_filepath, directory) 
        elif args[0] == '-r' or args[0] == '--remove':
            notes_remove_dir(cfg_filepath, directory)
    elif len(args) == 1:
        pattern = re.compile(args[0])
        cmp_similar(cfg_filepath, pattern)
    else: 
        print_usage()
