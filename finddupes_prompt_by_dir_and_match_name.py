import os
import argparse
import filecmp


description = """
Search provided directories. When a dupe is found (name and size match) the user is prompted to select a file to keep. Remember choice if other files
in same directories are found to be the same
"""

parser = argparse.ArgumentParser(description='description')
parser.add_argument('--d', required=True, action="append")
parser.add_argument('--dryrun', action='store_true')
parser.add_argument('--force', action='store_true')

args = parser.parse_args()
print(args)

if not args.dryrun and not args.force:
    user_continue = input("WARNING this is not a dry run. If dupes are found they will be deleted. Enter '1' to quit now.")
    if user_continue == '1':
        exit()

found = {}
known_paths = {}


def remove_a_file(path0, path1, filename, userinput):
    chosen_file = os.path.join(path0, filename) if userinput == "0" else os.path.join(path1, filename)
    try:
        if filecmp.cmp(os.path.join(path0, filename), os.path.join(path1, filename), shallow=False):
            if not args.dryrun:
                os.remove(chosen_file)
        else:
            print('Files are not equal. Aborting delete..')
    except FileNotFoundError:
        print("could not remove %s"%chosen_file)
    except EnvironmentError:
        print("could not remove %s"%chosen_file)


for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            if (name, size) in found:
                
                print(name, size, found[(name, size)], dirpath)
                if (found[(name, size)], dirpath) in known_paths:
                    choice = known_paths[(found[(name, size)], dirpath)]
                    remove_a_file(path0=found[(name, size)], path1=dirpath, filename=name, userinput=choice)
                    if choice == '0':
                        found[(name, size)] = dirpath
                else:
                    if filecmp.cmp( os.path.join(found[(name, size)], name), os.path.join(dirpath, name), shallow=False):

                        userinput = ""
                        while userinput not in ['0', '1', '2']:
                            print("enter 0 to delete %s" % os.path.join(found[(name, size)], name ))
                            print("enter 1 to delete %s" % os.path.join(dirpath, name ))
                            userinput = input("your choice (2 to skip): ")
                        if userinput == '2':
                            continue
                        known_paths[ (found[(name, size)], dirpath)] = userinput
                        remove_a_file(path0=found[(name, size)], path1=dirpath, filename=name, userinput=userinput)
                        if userinput == '0':
                            found[(name, size)] = dirpath

            else:
                found[(name, size)] = dirpath

