#!/usr/bin/env python3
import argparse

from finddupes import call


if __name__ == "__main__":
    description = ""
    parser = argparse.ArgumentParser(description=description )
    parser.add_argument('script', help="directory where to look for dupes")
    args, unknown = parser.parse_known_args()

    if args.script == 'finddupes':
        call(unknown)
    else:
        print('no such commands')
