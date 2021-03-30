#!/usr/bin/env python3

import os
import argparse
import filecmp
import hashlib
import sys
from collections import deque

from uwalk import uwalk


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


def remove_a_file(path0, path1, userinput):
    chosen_file = path0 if userinput == 0 else path1
    try:
        if not args.dryrun:
            os.remove(chosen_file)
    except FileNotFoundError:
        print("ERROR could not find %s"%chosen_file)
    except EnvironmentError:
        print("ERROR could not remove %s"%chosen_file)


def main(args):
        
    if not args.dryrun and not args.force:
        user_continue = input("WARNING this is not a dry run. If dupes are found they will be deleted. Enter '1' to quit now.")
        if user_continue == '1':
            exit()
    if args.dryrun:
        print('DRY RUN')

    args.dont_explore_paths = [os.path.normpath(x) for x in args.dont_explore_paths]

    found = {} # holds [file path, <bool>] where the bool indicates if path in hashes
    known_paths = {} # holds choices
    hashes = {} # holds file paths

    number_of_files_deleted = 0
    size_of_files_deleted = 0

    for path in args.d:
        for dirpath, dirnames, files in uwalk(path,
                start_at=args.start_at_dir,
                dont_explore_names=args.dont_explore_names, 
                dont_explore_paths=args.dont_explore_paths):
                
            dupes_by_dir = {}
            for name in files:
                if name in args.ignore_file_names:
                    continue
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
                        dupes_by_dir.setdefault(os.path.dirname(other_file), []).append((other_file, file_path, file_hash))
                    else:
                        hashes[file_hash] = file_path
                else:
                    if not args.ignore_zero_size or criteria != 0:
                        found[criteria] = [file_path, False]
            for destination_dir, matches in dupes_by_dir.items():
                print("=========================")
                print("1: match dir  : %s" % os.path.dirname(matches[0][0]))
                print("2: current dir: %s" % os.path.dirname(matches[0][1]))
                print("--")
                for match in matches:
                    print("%s | %s" % (match[0], match[1]))
                userinput = ""
                while userinput not in ['1', '2', 'e']:
                    userinput = input("choose file to keep by directory 1 or 2 (e to skip): ")
                if userinput == 'e':
                    continue
                for match in matches:
                    if not filecmp.cmp(match[0], match[1]):
                        print('files not equal %s | %s'%(match[0], match[1]))
                        continue
                    del_file_idx = 0 if userinput =='2' else 1
                    print("deleting %s"%match[del_file_idx])
                    number_of_files_deleted += 1
                    size_of_files_deleted += os.stat(match[del_file_idx]).st_size
                    remove_a_file(match[0], match[1], del_file_idx)
                    if userinput == '2': # keep
                        hashes[match[2]] = match[1]

    print("number of files deleted: %s" % number_of_files_deleted)
    print("size of files deleted: %s" % size_of_files_deleted)


description = """
Search provided directories. Find first by matching on size and then
by hash. Search for other dupes between same directories and report together.
Prompt user to choose one directory or thhe other (or skip).
"""


def call(source, arguments):
    parser = argparse.ArgumentParser(prog=source, description=description)
    parser.add_argument('--d', required=True, action="append")
    parser.add_argument('--dryrun', action='store_true')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--ignore_zero_size', action='store_true', help='ignore files with zero size')
    parser.add_argument('-n', '--dont_explore_names', action="append", help='directory names not to descend into e.g. .git', default=[])
    parser.add_argument('-p', '--dont_explore_paths', action="append", help='directory paths not to descend into e.g. ./a/b/c', default=[])
    parser.add_argument('-f', '--ignore_file_names', action="append", help="ignore all files with the specified name", default=[])
    parser.add_argument('-s', '--start_at_dir', help="Don't process any files before this file is found. Useful for restarting an interupted run.", default=None)
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    call(sys.argv[0], sys.argv[1:])
