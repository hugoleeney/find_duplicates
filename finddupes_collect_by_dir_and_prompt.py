#!/usr/bin/env python3

import os
import argparse
import filecmp
import hashlib
from collections import deque


description = """
Search provided directories. Find first by matching on size and then
by hash. Search for other dupes between same directories and report together.
Prompt user to choose one directory or thhe other (or skip).
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--d', required=True, action="append")
parser.add_argument('--dryrun', action='store_true')
parser.add_argument('--force', action='store_true')
parser.add_argument('--ignore_zero_size', action='store_true', help='ignore files with zero size')
parser.add_argument('-n', '--dont_explore_names', action="append", help='directory names not to descend into e.g. .git', default=[])
parser.add_argument('-p', '--dont_explore_paths', action="append", help='directory paths not to descend into e.g. ./a/b/c', default=[])
parser.add_argument('-f', '--ignore_file_names', action="append", help="ignore all files with the specified name", default=[])
parser.add_argument('-s', '--start_at_dir', help="Don't process any files before this file is found. Useful for restarting an interupted run.", default=None)
args = parser.parse_args()


if not args.dryrun and not args.force:
    user_continue = input("WARNING this is not a dry run. If dupes are found they will be deleted. Enter '1' to quit now.")
    if user_continue == '1':
        exit()
args.dont_explore_paths = [os.path.normpath(x) for x in args.dont_explore_paths]

 
def uwalk(top, topdown=True, onerror=None, followlinks=False, start_at=None,
        dont_explore_names=[], dont_explore_paths=[]):
    """
    Same function as os.walk but with extra features.
    start_at: don't yield any files until this directory path is reached
    dont_explore_names: don't yield any files with these names
    dont_explore_paths: don't yield any files in this sub-directory
    """

    process = True
    if start_at:
        process = False

    top = os.fspath(top)
    dirs = []
    nondirs = []
    walk_dirs = []

    try:
        scandir_it = os.scandir(top)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    with scandir_it:
        while True:
            try:
                try:
                    entry = next(scandir_it)
                except StopIteration:
                    break
            except OSError as error:
                if onerror is not None:
                    onerror(error)
                return

            try:
                is_dir = entry.is_dir()
            except OSError:
                is_dir = False

            if is_dir:
                dirs.append(entry.name)
            else:
                nondirs.append(entry.name)

            if not topdown and is_dir:
                if followlinks:
                    walk_into = True
                else:
                    try:
                        is_symlink = entry.is_symlink()
                    except OSError:
                        is_symlink = False
                    walk_into = not is_symlink

                if walk_into and entry.name not in dont_explore_names and \
                        entry.path not in dont_explore_paths:
                    walk_dirs.append(entry.path)

    if topdown:
        if not start_at:
            yield top, dirs, nondirs
        islink, join = os.path.islink, os.path.join
        for dirname in dirs:
            
            new_path = os.path.normpath(os.path.join(top, dirname))
            if start_at and new_path == start_at:
                start_at = None
                process = True

            if not process and start_at and start_at.startswith(new_path):
                process = True

            new_path = join(top, dirname)
            if (followlinks or not islink(new_path))  and \
                    dirname not in dont_explore_names and \
                    os.path.normpath(new_path) not in dont_explore_paths and \
                    process:
                yield from uwalk(new_path, topdown, onerror, followlinks, start_at, dont_explore_names, dont_explore_paths)
            
            if process:
                start_at = None
    else:
        for new_path in walk_dirs:
            
            new_path = os.path.normpath(new_path)
            if start_at and new_path == start_at:
                start_at = None
                process = True
            if not process and start_at and start_at.startswith(new_path):
                process = True

            if os.path.basename(new_path) not in dont_explore_names and \
                    os.path.normpath(new_path) not in dont_explore_paths and \
                    process:
                yield from uwalk(new_path, topdown, onerror, followlinks, start_at, dont_explore_names, dont_explore_paths)
            if process:
                start_at = None

        if not start_at:
            yield top, dirs, nondirs


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
