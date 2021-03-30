#!/usr/bin/env python3

import json
import os
import argparse
import pathlib
import filecmp
import hashlib
import sys

from uwalk import uwalk


description = """
Traverse provided directory and build a directory of hash codes to files.
"""


def get_file_md5(file_path):
    with open(file_path, 'rb') as opened_file:
        readFile = opened_file.read()
        md5Hash = hashlib.md5(readFile)
        md5Hashed = md5Hash.hexdigest()
        return md5Hashed


def main(args):
    d = {}
    for dirpath, dirnames, files in os.walk(args.d):
        for name in files:
            file_path = os.path.join(dirpath, name)
            d.setdefault(get_file_md5(file_path), []).append(file_path)


    if os.path.isfile(args.output_file) and not args.force:
        userinput = 'a'
        while userinput.lower() not in ['y', 'n', '']:
            userinput = input('The output file specified already exists. Do you want to overwrite? [Y/n]')
        if userinput == 'n':
            print('exiting..')
            exit()

    with open(args.output_file, 'w') as of:
        json.dump(d, of)


def call(source, arguments):
    parser = argparse.ArgumentParser(prog=source, description=description) 
    parser.add_argument('--d', required=True, help="a directory to look in")
    parser.add_argument('-n', '--dont_explore_names', action="append", default=[], help="directory names not to descend into")
    parser.add_argument('-p', '--dont_explore_paths', action="append", default=[], help="directory paths not to descend into")
    parser.add_argument('-o', '--output_file', default='.hashdir.json', help='name of the file to output')
    parser.add_argument('-f', '--force', action='store_true', help='dont ask to overwrite existing output file')
    args = parser.parse_args(arguments)
    main(args)


if __name__ == "__main__":
    call(sys.argv[0], sys.argv[1:])
