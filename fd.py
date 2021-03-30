#!/usr/bin/env python3
import argparse
import sys

import finddupes


if __name__ == "__main__":
    description = ""
    parser = argparse.ArgumentParser(description=description )
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser_finddupes = subparsers.add_parser('finddupes', help=finddupes.description)
    finddupes.add_arguments(parser_finddupes)
    parser_finddupes.set_defaults(func=finddupes.main)
    
    args = parser.parse_args()

    print(args.command)
    args.func(args)
