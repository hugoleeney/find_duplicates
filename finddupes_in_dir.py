#!/usr/bin/env python3

import os
import argparse
import filecmp
import hashlib
import sys

from uwalk import uwalk


description = """
Any files found in '--dir' that are dupes of files found in '--d' directories 
will be deleted without prompt.
"""


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


class DupeFinder():

    def __init__(self, ignore_zero_size):
        self.found = {}
        self.sizes_done = set()
        self.hashes = {}
        self.ignore_zero_size = ignore_zero_size

    def add_file(self, file_path):
        size = os.path.getsize(file_path)
        if not self.ignore_zero_size or size != 0:
            self.found.setdefault(size, []).append(file_path)

    def prep_size(self, size):
        if size in self.found:
            if size not in self.sizes_done:
                size_matches = self.found.get(size)
                for match in size_matches:
                    hash = get_file_md5(match)
                    self.hashes.setdefault(hash, []).append(match)
                self.sizes_done.add(size)
            return True
        else:
            return False
    
    def is_dupe(self, dir_file_path):
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


def main(args):

    print("looking for dupes, deleting from %s"%args.dir)


    if not args.dryrun and not args.force:
        user_continue = input('WARNING this is not a dry run. Any dupes found will be deleted without any prompt. Enter 1 to quit now.')
        if user_continue == '1':
            exit()
    else:
        print("DRY RUN")

    # process files from the '--d' args and create lookup structure
    dupe_finder = DupeFinder(args.ignore_zero_size)
    for path in args.d:
        for dirpath, dirnames, files in uwalk(path, 
                dont_explore_names=args.dont_explore_names,
                dont_explore_paths=args.dont_explore_paths):
            for name in files:
                file_path = os.path.join(dirpath, name)
                dupe_finder.add_file(file_path)


    # process files from the '--dir' arg and delete any that exist in lookup structure
    for dirpath, dirnames, files in uwalk(args.dir, 
            dont_explore_names=args.dont_explore_names,
            dont_explore_paths=args.dont_explore_paths):
        for name in files:
            dir_file_path = os.path.join(dirpath, name)
            size = os.path.getsize(dir_file_path)
            if not args.ignore_zero_size or size != 0:
                match = dir_file_matched(dir_file_path, dupe_finder)
                if match:
                    print("============================")
                    print("Name: %s, %s" % (name, size))
                    print('             ', '"%s"' % match)
                    print('will delete :', '"%s"' % dir_file_path)
                    # print(name, size, '"%s"'%match, '"%s"'%dirpath, "will delete %s" % dir_file_path)
                    try:
                        if not args.dryrun:
                            os.remove(os.path.join(dirpath, name))
                    except EnvironmentError as e:
                        print("ERROR deleting %s"%os.path.join(dirpath, name))


def call(source, arguments):
    parser = argparse.ArgumentParser(prog=source, description=description) 
    parser.add_argument('--d', required=True, action="append", help="where to look for 'originals', multiple instances accepted")
    parser.add_argument('--dir', required=True, help='where to look for dupes')
    parser.add_argument('--dryrun', action='store_true', help='just look for dupes, does not delete files')
    parser.add_argument('--force', action='store_true', help='do not ask for confirmation to proceed')
    parser.add_argument('-n', '--dont_explore_names', action='append', help='directory names not to explore e.g. .git', default=[])
    parser.add_argument('-p', '--dont_explore_paths', action='append', help='directory paths not to explore e.g. .git', default=[])
    parser.add_argument('--ignore_zero_size', action='store_true', help='ignore any file with zero size')
    args = parser.parse_args(arguments)
    main(args)


if __name__ == "__main__":
    call(sys.argv[0], sys.argv[1:])
