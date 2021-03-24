import os
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--d', action="append")
parser.add_argument('--dir')
parser.add_argument('--dryrun', action='store_true')

args = parser.parse_args()
print(args)


found = {}
for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            found[(name, size)] = dirpath

for dirpath, dirnames, files in os.walk(args.dir):
    for name in files:
        size = os.path.getsize(os.path.join(dirpath, name))
        if (name, size) in found:
            print(name, size, '"%s"'%found[(name, size)], '"%s"'%dirpath, "will delete %s"%os.path.join(dirpath,name))
            if not args.dryrun:
                try:
                    os.remove(os.path.join(dirpath, name))
                except EnvironmentError as e:
                    print("ERROR deleting %s"%os.path.join(dirpath, name))


