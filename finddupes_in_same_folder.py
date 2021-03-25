import os
import argparse
import pathlib
import filecmp
import hashlib


description = """
Look for duplicate files in a single folder - traverses entire directory
hierarchy. Candidates are files are first found by size and the by hash but
will not be deleted unless the files are an exact match. User will be prompted 
to choose a file to keep unless '--auto' option is used. '--auto' option will 
delete the file with the shortest name or the first file found. It is not 
reccomended to run this utility in directories containing software distributions
or code as such folders often contain necessary duplicates.
"""
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--d', required=True, action="append", help="a directory to look in, multiple instances accepted")
parser.add_argument('--dryrun', action='store_true', help="do a dry run, do not perform any deletions")
parser.add_argument('--auto', action='store_true', help="do not prompt user to choose file")
parser.add_argument('--force', action='store_true', help="do not ask for confirmation to proceed when not dry runs")
args = parser.parse_args()
print(args)

if not args.dryrun and not args.force:
    user_continue = input("WARNING this is not a dry run. Any dupes found will be delete. Enter '1' now to exit.")
    if user_continue == '1':
        exit()


def delete_dupe(f, to_keep, args):
    if not filecmp.cmp(to_keep, f):
        print('%s not equal to chosen file'%f)
        return 0
    else:
        print('deleting %s: '%f)
        assert filecmp.cmp(to_keep, f)
        if not args.dryrun:
            os.remove(f)
        return 1


def get_user_input(allowed_responses, break_response, message):
    userinput = ''
    while userinput not in allowed_responses:
        try:
            userinput = input()
            if userinput == break_response:
                break
            userinput = int(userinput)
        except ValueError as e:
            print("enter value between 0 and %s"%len(files))
    return userinput


def print_files(criteria, files):
    print('---------------------------------------------')
    print('criteria: %s'%str(criteria))
    for i, f in enumerate(files):
        print(i, f)


number_of_dupes_deleted = 0

for path in args.d:
    for dirpath, dirnames, files in os.walk(path):

        # find candidates just be size first
        foundcandidates = {}
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            criteria = size
            foundcandidates.setdefault(criteria, []).append(os.path.join(dirpath, name))
        
        # process candidates by md5 hash
        found = {}
        for size, file_paths in foundcandidates.items():
            if len(file_paths) > 1:
                for file_path in file_paths:
                    with open(file_path, 'rb') as opened_file:
                        readFile = opened_file.read()
                        md5Hash = hashlib.md5(readFile)
                        md5Hashed = md5Hash.hexdigest()
                        found.setdefault(md5Hashed, []).append(file_path)
        
        # determine which file to keep and delete rest
        for criteria, files in found.items():
            if len(files) > 1:

                print_files(criteria, files)
                
                if args.auto:
                    
                    # choose which file to keep
                    if all( [len(f) == len(f[0]) for f in files] ):
                        to_keep = f[0]
                    else:
                        to_keep = min(files, key=lambda x: len(x))

                    for f in files:
                        if f != to_keep:
                            number_of_dupes_deleted += delete_dupe(f, to_keep, args)

                else:
                    userinput = get_user_input(list(range(len(files))), 's', "Enter number of file you want to keep (s to skip). We'll double check the files are exactly the same before deleting: ")
                    if userinput == 's':
                        continue
                    for i, f in enumerate(files):
                        if i != userinput:
                            number_of_dupes_deleted += delete_dupe(f, files[userinput], args)


print("number of dupes deleted: %s %s" % (number_of_dupes_deleted, "(dry run)" if args.dryrun else ""))



