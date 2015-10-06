#!/usr/bin/env python
import sys, re, os 
import subprocess
import json

def print_usage():
    '''
    print help messages
    '''
    print('usage: notes [--add | -a <path-to-directory>]')
    print('             [--delete | -d <path-to-directory>]')
    print('             [--show] [--update | -u]')
    print('             [--help | -h] [--list | -l]')
    # TODO
    # print('             [--search | -s]')
    print("             [search-key]")


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
    add a directory to Notes
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
    delete a directory from Notes
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


def file_list(cfg_filepath):
    '''
    list all files tracked by Notes
    '''
    with open(cfg_filepath, "r") as f:
        config = json.load(f)
        for key in config.keys():
            for file in config[key]:
                print(file)


def cmp_similar(cfg_filepath, str_pattern):
    '''
    search pattern from all filenames and then open the file,
    print candidates if more than one filename is matched
    '''
    pattern = re.compile(str_pattern, re.IGNORECASE)
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
            else: print('"' + str_pattern + '"' + " not find!")
    else:
        print("Not Configured!")


if __name__ == "__main__":
    # TODO
    # alias function
    # function of ignore
    args = sys.argv[1:]
    cfg_filepath = os.path.expanduser('~') + '/'+ ".notes_config"
    if len(args) == 2:
        directory = args[1]
        abs_directory = get_absolute_path(directory)
        # Add
        if args[0] == '-a' or args[0] == '--add':
            notes_add_dir(cfg_filepath, abs_directory) 
        # Delete
        elif args[0] == '-d' or args[0] == '--delete':
            notes_remove_dir(cfg_filepath, abs_directory, False)
        else:
            print('Unknown option: ' + args[0])
            print_usage()
    elif len(args) == 1:
        if args[0][0] != '-':
            cmp_similar(cfg_filepath, args[0])
        elif args[0] == '--show':
            # Show added directories
            with open(cfg_filepath, 'r') as f:
                config = json.load(f)
                for key in config.keys():
                    print(key)
        elif args[0] == '--update' or args[0] == '-u':
            # Update added directories 
            with open(cfg_filepath, 'r') as f:
                config = json.load(f)
                for key in config.keys():
                    notes_remove_dir(cfg_filepath, key, True)
                    notes_add_dir(cfg_filepath, key)
        elif args[0] == '-p' or args[0] == '--push':
            # Update remote repo
            with open(cfg_filepath, 'r') as f:
                config = json.load(f)
                for key in config.keys():
                    os.chdir(key)
                    subprocess.call('git push origin master', shell = True)
        elif args[0] == '-c' or args[0] == '--commit':
            # Update remote repo
            with open(cfg_filepath, 'r') as f:
                config = json.load(f)
                for key in config.keys():
                    os.chdir(key)
                    subprocess.call('git commit -a', shell = True)
        elif args[0] == '--list' or args[0] == '-l':
            # List all added files
            file_list(cfg_filepath)
        elif args[0] == '--help' or args[0] == '-h':
            # Print help messages
            print_usage()
        else: 
            print('Unknown option: ' + args[0])
            print_usage()
    else: 
        print_usage()
