#!/usr/bin/env python3
import argparse
import sys
from collections import namedtuple

import build_file_hashes
import find_all_dupes_then_prompt
import finddupes_collect_by_dir_and_prompt
import finddupes_in_dir
import finddupes_in_same_folder
import finddupes_prompt_by_dir_and_match_name
import finddupes_prompt_by_dir
import finddupes
import number_of_dupes_by_size_only
import number_of_dupes


if __name__ == "__main__":

    description = "Interface to run find dupes sub-commands. Run any sub-command with '-h' for more info."

    commands = {
        'build_hashdir': build_file_hashes.call,
        'find_all_then_prompt': find_all_dupes_then_prompt.call,
        'collect_by_dir': finddupes_collect_by_dir_and_prompt.call,
        'find_in_dir': finddupes_in_dir.call,
        'find_in_same_folder': finddupes_in_same_folder.call,
        'find_match_name_prompt_pairwise_by_dir': finddupes_prompt_by_dir_and_match_name.call,
        'find_prompt_pairwise_by_dir': finddupes_prompt_by_dir.call,
        'finddupes': finddupes.call,
        'report_size_dupes': number_of_dupes_by_size_only.call,
        'report_dupes': number_of_dupes.call
    }

    parser = argparse.ArgumentParser(description=description, add_help=False)
    parser.add_argument('command', help="sub-command you want to run from choice of %s."%", ".join(commands.keys()))
    parser.add_argument('-h', '--help', action='store_true', help='get help')
    # only display help for this script if it is the first argument
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args, unknown = parser.parse_known_args()
    if args.help:
        unknown.append('-h')

    func = commands[args.command]
    func("%s %s" % (parser.prog, args.command), unknown)
