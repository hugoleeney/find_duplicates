#!/usr/bin/env python3
import argparse
import sys
from collections import namedtuple
import finddupes
import build_file_hashes
import finddupes_collect_by_dir_and_prompt

if __name__ == "__main__":

    description = "interface to run find dupes sub-commands"

    commands = {
        'finddupes': finddupes.call,
        'build_hashdir': build_file_hashes.call,
        'collectbydir': finddupes_collect_by_dir_and_prompt.call
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
