import os
import argparse
import filecmp
import hashlib


description = """
Finds duplicate files and reports the total number in the specified directories.
"""
parser = argparse.ArgumentParser(description=description )
parser.add_argument('--d', required=True, action="append", help="directories where to look for dupes")
parser.add_argument('--show_progress', action="store_true", help="intermitently show the number of files that has been processed")
parser.add_argument('--show_dupes', action="store_true", help="show all of the dupes after processing")
args = parser.parse_args()


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


number_of_files = 0
found = {}


# count the number of files
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            number_of_files += 1
print("number of files: %s" % number_of_files)


# build the dupes structure
num_processed = 1
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        
        if os.path.dirname(dirpath) in ['.git', '.svn']:
            continue

        for name in files:

            if args.show_progress:
                if num_processed % 10000 == 0:
                    print('processed: %s' % num_processed)
                num_processed += 1

            filepath = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(filepath)
            except FileNotFoundError as fnfe:
                print('file not found %s'%filepath)
                continue
            criteria = size
            found.setdefault(criteria, []).append(filepath)


# sum the dupes and sizes and print if required
number_of_dupes = 0
size_of_dupes = 0
if args.show_dupes:
    for size, paths in found.items():
        number_of_dupes += len(paths)-1
        if len(paths) > 1:
            try:
                size_of_dupes += (size*(len(paths)-1))
            except FileNotFoundError as fnfe:
                print('file not found %s'%paths[0])
                continue
            print('--------------------------------')
            for p in paths:
                print(p)
else:
    for size, paths in found.items():
        number_of_dupes += len(paths)-1


# print final stats
print("number of size dupes found: %s" % number_of_dupes)
print("estimate size of dupes: %s" % size_of_dupes)
