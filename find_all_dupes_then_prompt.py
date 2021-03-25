#!/usr/bin/env python3

import os
import argparse
import filecmp
import hashlib
from collections import namedtuple


description = """
Finds duplicate files and reports the total number in the specified directories.
"""
parser = argparse.ArgumentParser(description=description )
parser.add_argument('--d', required=True, action="append", help="directories where to look for dupes")
parser.add_argument('--show_progress', action="store_true", help="intermitently show the number of files that has been processed")
parser.add_argument('--dryrun', action='store_true', help="program will run but no files will be deleted")
args = parser.parse_args()


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


number_of_files = 0
found = {}
hashes = {}


# count the number of files
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            number_of_files += 1
print("number of files: %s" % number_of_files)


# build the dupes structure
num_processed = 1
FoundEntry = namedtuple('FoundEntry', ['file', 'processed'])
# totalhashes = 0
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:

            if args.show_progress:
                if num_processed % 10000 == 0:
                    print('processed: %s' % num_processed)
                num_processed += 1

            filepath = os.path.join(dirpath, name)
            size = os.path.getsize(filepath)
            criteria = size
            if criteria in found:
                if not found[criteria].processed:
                    first_hash = get_file_md5(found[criteria][0])
                    hashes.setdefault(first_hash, []).append(found[criteria][0])
                    found[criteria] = FoundEntry('', True)
                file_hash = get_file_md5(filepath)
                hashes.setdefault(file_hash, []).append(filepath)
            else:
                found[criteria] = FoundEntry(filepath, False)


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
        except ValueError as e:
            print("enter value between 0 and %s"%len(files))
    return userinput


# count dupes and sum sizes
number_of_dupes = 0
size_of_dupes = 0
for filehash, paths in hashes.items():
    number_of_dupes += len(paths)-1
    if len(paths) > 1:
        size_of_dupes += (os.path.getsize(paths[0])*(len(paths)-1))
print("number of dupes found: {:,}".format(number_of_dupes))
print("estimate size of dupes: {:,}".format(size_of_dupes))

# process dupes
number_of_dupes_deleted = 0
size_of_dupes_deleted = 0
for filehash, files in hashes.items():
    if len(files) > 1:
        print('--------------------------------')
        for i, f in enumerate(files):
            print(i, f)
        userinput = get_user_input(list(range(len(files))), 's', "Enter number of file you want to keep (s to skip). We'll double check the files are exactly the same before deleting: ")
        if userinput == 's':
            continue
        for i, f in enumerate(files):
            if i != userinput:
                deleted = delete_dupe(f, files[userinput], args)
                number_of_dupes_deleted += deleted
                if deleted:
                    size_of_dupes_deleted += os.path.getsize(f)


# print final stats
print("number of dupes deleted: {:,}".format(number_of_dupes_deleted))
print("estimate size of dupes deleted: {:,}".format(size_of_dupes_deleted))

