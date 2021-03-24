import os
import argparse


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--d', action="append")
parser.add_argument('--criteria', default='ns')

args = parser.parse_args()
print(args)


def get_criteria(**kw):
    mapd = { 'n': 'name', 's': 'size', 't': 'type' }
    result = []
    for c in 'ns':
        if c in args.criteria:
            if c == 't':
                result.append( os.path.splitext(kw['name'])[1] )
            else:
                result.append( kw[mapd[c]] )
    return tuple(result)


found = {}

for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            criteria = get_criteria(name=name, size=size)
            if criteria in found:
                print(name, size, found[criteria], dirpath)
            else:
                found[criteria] = dirpath

