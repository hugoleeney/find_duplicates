import os
import argparse
import filecmp
import hashlib

description = """
Search provided directories. Find first by matching on size and then
by hash. For found dupes prompt the user to select a file to keep. 
Remember the choice if other dupes in same directories are found.
"""
parser = argparse.ArgumentParser(description='description')
parser.add_argument('--d', required=True, action="append")
parser.add_argument('--dryrun', action='store_true')
parser.add_argument('--force', action='store_true')
args = parser.parse_args()


if not args.dryrun and not args.force:
    user_continue = input("WARNING this is not a dry run. If dupes are found they will be deleted. Enter '1' to quit now.")
    if user_continue == '1':
        exit()

 
def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


def remove_a_file(path0, path1, userinput):
    chosen_file = path0 if userinput == "0" else path1
    try:
        if not args.dryrun:
            os.remove(chosen_file)
    except EnvironmentError as e:
        print("ERROR could not remove %s"%chosen_file)
    except FileNotFoundError as fnfe:
        print("ERROR could not remove %s"%chosen_file)


found = {} # holds [file path, <bool>] where the bool indicates if path in hashes
known_paths = {} # holds choices
hashes = {} # holds file paths

for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            file_path = os.path.join(dirpath, name)
            size = os.path.getsize(file_path)
            criteria = size
            if criteria in found: # matched on size, continue to find based on hash

                # if the other side of the match has not been hashed do it now
                if not found[criteria][1]:
                    hashes[get_file_md5(found[criteria][0])] = found[criteria][0]
                    found[criteria][1] = True
                
                # hash the current file ready to match
                file_hash = get_file_md5(file_path)

                # match the current file
                if file_hash in hashes:
                    other_file = hashes[file_hash]
                    print(other_file, '|', file_path)
                    other_dir = os.path.dirname(other_file)
                    
                    if filecmp.cmp(other_file, file_path, shallow=False):
                        if (other_dir, dirpath) in known_paths:
                            print('using known paths...')
                            choice = known_paths[(other_dir, dirpath)]
                            remove_a_file(other_file, file_path, choice)
                            if choice == '0':
                                hashes[file_hash] = dirpath
                        else:
                            userinput = ""
                            while userinput not in ['0', '1', '2']:
                                print("enter 0 to delete %s" % other_file)
                                print("enter 1 to delete %s" % file_path)
                                userinput = input("your choice (2 to skip): ")
                            if userinput == '2':
                                continue
                            known_paths[ (other_dir, dirpath)] = userinput
                            remove_a_file(other_file, file_path, userinput)
                            if userinput == '0':
                                hashes[file_hash] = file_path
                                print('found updated with %s' % file_path)
                    else:
                        print("files not same, aborting delete")
            else:
                found[criteria] = [file_path, False]

