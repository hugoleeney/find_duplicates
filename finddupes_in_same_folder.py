#!/usr/bin/env python3

import os
import argparse
import pathlib
import filecmp
import hashlib
from uwalk import uwalk


description = """
Look for duplicate files in a single folder - traverses entire directory
hierarchy. Candidates files are first found by size and then by hash. Files
with 0 size are not considered. Files
will not be deleted unless the files are an exact match. User will be prompted 
to choose a file to keep unless '--auto' option is used. '--auto' option will 
delete the file with the shortest name or the first file found. It is not 
reccomended to run this utility in directories containing software distributions
or code as such folders often contain necessary duplicates.
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--d', required=True, action="append", help="a directory to look in, multiple instances accepted")
parser.add_argument('--dryrun', action='store_true', help="do a dry run, do not perform any deletions")
parser.add_argument('--auto', action='store_true', help="do not prompt user to choose file")
parser.add_argument('--force', action='store_true', help="do not ask for confirmation to proceed when not dry runs")
parser.add_argument('--dont_recurse', action='store_true', help='do not recurse into sub directories')
parser.add_argument('-n', '--dont_explore_names', action="append", default=[], help="directory names not to descend into")
parser.add_argument('-p', '--dont_explore_paths', action="append", default=[], help="directory paths not to descend into")
parser.add_argument('-s', '--start_at', help="a directory where to start looking, if not found no files will be processed (n.b --dont_explore_paths)", default=None)
args = parser.parse_args()


if not args.dryrun and not args.force:
    user_continue = input("WARNING this is not a dry run. Any dupes found will be deleted. Enter '1' now to exit.")
    if user_continue == '1':
        exit()
args.dont_explore_paths = [os.path.normpath(x) for x in args.dont_explore_paths]
args.start_at = os.path.normpath(args.start_at)


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
            userinput = input(message)
            if userinput == break_response:
                break
            userinput = int(userinput)
        except ValueError:
            print("enter value between 0 and %s"%len(files))
    return userinput


def print_files(criteria, files):
    print('---------------------------------------------')
    print('criteria: %s'%str(criteria))
    for i, f in enumerate(files):
        print(i+1, f)


number_of_dupes_deleted = 0

for path in args.d:
    for dirpath, dirnames, files in uwalk(path, start_at=args.start_at, dont_explore_names=args.dont_explore_names, dont_explore_paths=args.dont_explore_paths):

        # find candidates just be size first
        foundcandidates = {}
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            if size != 0:
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
                    userinput = get_user_input(list(range(1, len(files)+1)), 'e', "Enter number of file you want to keep ('e' to skip). We'll double check the files are exactly the same before deleting: ")
                    if userinput == 'e':
                        continue
                    for i, f in enumerate(files):
                        if i+1 != userinput:
                            number_of_dupes_deleted += delete_dupe(f, files[userinput-1], args)

        if args.dont_recurse:
            break


print("number of dupes deleted: %s %s" % (number_of_dupes_deleted, "(dry run)" if args.dryrun else ""))



