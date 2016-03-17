#!/usr/bin/env python
"""NOTES
Usage:
  notes.py (-a | --add) <ADD_DIRS>...
  notes.py (-d | --delete) <DEL_DIRS>...
  notes.py <search-key>
  notes.py [-l | --list] [--show]
  notes.py -u | --update
  notes.py -p | --push
  notes.py -c | --commit
  notes.py -h | --help
  notes.py --version

Options:
  -h --help     Show this screen
  -a --add      Add directories to be traced
  -d --delete   Add directories to be traced
  -u --update   Update current files
  -p --push     Push current files being traced to remote repo
  -c --commit   Git commit current files being traced
  -l --list     Show all files being traced
  --show        Show all directories being traced
  --version     Show version
"""
import sys, re, os 
import subprocess
import json
from docopt import docopt

# TODO
# print('             [--search | -s]')

def get_absolute_path(directory):
    '''
    return absolute path of the given directory
    '''
    if directory[0] == '/':
        return directory 
    else:
        return os.getcwd() + "/" + directory 


def search_file(L, dir):
    '''
    search file that ends with '.md' and append it to L
    '''
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".md"):
                L.append(os.path.join(root, file).replace(dir, '', 1))
    

def notes_add_dir(cfg_filepath, add_dir):
    '''
    add directories to Notes
    '''
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            config = json.load(f)
        if add_dir in config:
            print(add_dir + " has been added!")
        elif not os.path.exists(add_dir):
            print("No such directory!")
        else:
            with open(cfg_filepath, "w") as f:
                config[add_dir] = []
                search_file(config[add_dir], add_dir)
                json.dump(config, f)
    else:
        with open(cfg_filepath, "w") as f:
            config = {add_dir:[]}
            search_file(config[add_dir], add_dir)
            json.dump(config, f)


def notes_remove_dir(cfg_filepath, remove_dir, is_update):
    '''
    delete directories from Notes
    '''
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            config = json.load(f)
        if remove_dir not in config:
            print(remove_dir + "has not neen added!")
        else:
            with open(cfg_filepath, "w") as f:
                del config[remove_dir]
                json.dump(config, f)
            if is_update:
                print(remove_dir + " updated")
            else:
                print(remove_dir + " removed")
    else:
        print("Not Configured!")


def files_iteration(cfg_filepath, mode, str_pattern):
    '''
    itertate files being traced
    operations: search, update, list, show, push, commit
    '''
    if(os.path.exists(cfg_filepath)):
        with open(cfg_filepath, "r") as f:
            config = json.load(f)
            pattern = re.compile(str_pattern, re.IGNORECASE)
            candis = []
            for key in config.keys():
                if(mode == 'search'):
                    for file in config[key]:
                        if pattern.search(file.split('.')[-2]):
                            if not os.path.exists(key + file):
                                print('File corruption')
                                print('Please check ' + key)
                                exit()
                            else:
                                candis.append(key + file)
                if(mode == 'list'):
                # list all files tracked by Notes
                    for file in config[key]:
                        print(file)
                elif(mode == 'update'):
                    # Update added directories 
                    notes_remove_dir(cfg_filepath, key, True)
                    notes_add_dir(cfg_filepath, key)
                elif(mode == 'show'):
                # Show added directories
                    print(key)
                elif(mode == 'push'):
                    # Update remote repo
                    os.chdir(key)
                    subprocess.call('git push origin master', shell = True)
                elif(mode == 'commit'):
                    # Update remote repo
                    os.chdir(key)
                    subprocess.call('git commit -a', shell = True)

            if(mode == 'search'):
                if len(candis) == 1:
                    subprocess.call('vim ' + candis[0], shell = True)
                elif len(candis) > 1:
                    print("There are some files you may want to access:")
                    for candi in candis:
                        print(candi)
                else: print('"' + str_pattern + '"' + " not find!")
    else:
        print("Not Configured!")


if __name__ == "__main__":
    # TODO
    # alias function
    # function of ignore
    args = docopt(__doc__, version='1.0')
    cfg_filepath = os.path.expanduser('~') + '/'+ ".notes_config"

    if(args['<search-key>']):
        files_iteration(cfg_filepath, 'search', args['<search-key>'])
    elif(args['--update']):
        files_iteration(cfg_filepath, 'update', "")
    elif(args['--push']):
        files_iteration(cfg_filepath, 'push', "")
    elif(args['--commit']):
        files_iteration(cfg_filepath, 'commit', "")
    elif(args['--add']):
        for dir in args['<ADD_DIRS>']:
            notes_add_dir(cfg_filepath, get_absolute_path(dir))
    elif(args['--delete']):
        for dir in args['<DEL_DIRS>']:
            notes_add_dir(cfg_filepath, get_absolute_path(dir)) 
    elif(args['--list']):
        files_iteration(cfg_filepath, 'list', "")
    elif(args['--show']):
        files_iteration(cfg_filepath, 'show', "")
