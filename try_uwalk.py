import argparse
from uwalk import uwalk


parser = argparse.ArgumentParser(description="")
parser.add_argument('-b', '--bottomup', action="store_true", help="walk bottom up")
parser.add_argument('-s', '--start_at', help='path where to start')
parser.add_argument('-p', '--dont_explore_paths', action="append", default=[], help="directory paths not to descend into")
args = parser.parse_args()


for f in uwalk('./', not args.bottomup, start_at=args.start_at, dont_explore_paths=args.dont_explore_paths):
    print(f)
