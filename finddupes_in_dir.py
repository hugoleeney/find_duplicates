#!/usr/bin/env python3

import os
import argparse
import filecmp


description = """
Any files found in '--dir' that are dupes of files found in '--d' directories will be deleted without prompt.
"""
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--d', action="append", help="where to look for 'originals', multiple instances accepted")
parser.add_argument('--dir', help='where to look for dupes')
parser.add_argument('--dryrun', action='store_true', help='just look for dupes, does not delete files')
parser.add_argument('--force', action='store_true', help='do not ask for confirmation to proceed')
args = parser.parse_args()
print("looking for dupes, deleting from %s"%args.dir)


if not args.dryrun and not force:
    user_continue = input('WARNING this is not a dry run. Any dupes found will be deleted. Enter 1 to quit now.')
    if user_continue == '1':
        exit()


# process files from the '--d' args and create lookup structure
found = {}
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            found[(name, size)] = dirpath

# process files from the '--dir' arg and delete any that exist in lookup structure
for dirpath, dirnames, files in os.walk(args.dir):
    for name in files:
        size = os.path.getsize(os.path.join(dirpath, name))
        if (name, size) in found:
            print(name, size, '"%s"'%found[(name, size)], '"%s"'%dirpath, "will delete %s"%os.path.join(dirpath,name))
            try:
                if filecmp.cmp(os.path.join(found[(name, size)], name), os.path.join(dirpath, name), shallow=False):
                    if not args.dryrun:
                        os.remove(os.path.join(dirpath, name))
                else:
                    print('File contents not the same. Aborting delete.')
            except EnvironmentError as e:
                print("ERROR deleting %s"%os.path.join(dirpath, name))
