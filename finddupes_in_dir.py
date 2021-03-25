#!/usr/bin/env python3

import os
import argparse
import filecmp
import hashlib

description = """
Any files found in '--dir' that are dupes of files found in '--d' directories 
will be deleted without prompt.
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--d', required=True, action="append", help="where to look for 'originals', multiple instances accepted")
parser.add_argument('--dir', required=True, help='where to look for dupes')
parser.add_argument('--dryrun', action='store_true', help='just look for dupes, does not delete files')
parser.add_argument('--force', action='store_true', help='do not ask for confirmation to proceed')
args = parser.parse_args()
print("looking for dupes, deleting from %s"%args.dir)


if not args.dryrun and not args.force:
    user_continue = input('WARNING this is not a dry run. Any dupes found will be deleted. Enter 1 to quit now.')
    if user_continue == '1':
        exit()


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


class DupeFinder():

    def __init__(self):
        self.found = {}
        self.hashes = {}

    def add_file(self, file_path):
        size = os.path.getsize(file_path)
        self.found.setdefault(size, []).append(file_path)

    def prep_size(self, size):
        if size in self.found:
            size_matches = self.found.get(size)
            for match in size_matches:
                hash = get_file_md5(match)
                self.hashes.setdefault(hash, []).append(match)
            return True
        else:
            return False
    
    def is_dupe(self, file_path):
        dir_file_hash = get_file_md5(dir_file_path)
        possibles = self.hashes.get(dir_file_hash, [])
        for p in possibles:
            if filecmp.cmp(dir_file_path, p):
                return p
        return None
        
            
def dir_file_matched(dir_file_path, dupe_finder):
    size = os.path.getsize(dir_file_path)
    if dupe_finder.prep_size(size):
        return dupe_finder.is_dupe(dir_file_path)
    else:
        return None


# process files from the '--d' args and create lookup structure
dupe_finder = DupeFinder()
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            file_path = os.path.join(dirpath, name)
            dupe_finder.add_file(file_path)


# process files from the '--dir' arg and delete any that exist in lookup structure
for dirpath, dirnames, files in os.walk(args.dir):
    for name in files:
        dir_file_path = os.path.join(dirpath, name)
        match = dir_file_matched(dir_file_path, dupe_finder)
        if match:
            size = os.path.getsize(dir_file_path)
            print(name, size, '"%s"'%match, '"%s"'%dirpath, "will delete %s" % dir_file_path)
            try:
                if not args.dryrun:
                    os.remove(os.path.join(dirpath, name))
            except EnvironmentError as e:
                print("ERROR deleting %s"%os.path.join(dirpath, name))
