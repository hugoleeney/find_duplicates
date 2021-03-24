import os
import argparse
import pathlib
import filecmp


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--d', action="append")
parser.add_argument('--dryrun', action='store_true')
parser.add_argument('--auto', action='store_true')


args = parser.parse_args()
print(args)


file_types_to_skip = ['bmp']


for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        found = {}
        for name in files:
            size = os.path.getsize(os.path.join(dirpath, name))
            fname = pathlib.Path(os.path.join(dirpath, name))
            t = fname.stat().st_ctime
            # criteria = [x for x in os.stat(os.path.join(dirpath,name))]
            criteria = (size, t)
            # criteria.append(os.path.splitext(name)[1].lower())
            # criteria = tuple(criteria)
            found.setdefault(criteria, []).append(os.path.join(dirpath, name))
        for criteria, files in found.items():
            if len(files) > 1:
                print('---------------------------------')
                print('criteria: %s'%str(criteria))
                for i, f in enumerate(files):
                    print(i, f)
                userinput = ''
                if args.auto:
                    if all( [len(f) == len(f[0]) for f in files] ):
                        to_keep = f[0]
                    else:
                        to_keep = min(files, key=lambda x: len(x))
                    for f in files:
                        if f != to_keep and os.path.splitext(f)[1].lower() not in file_types_to_skip:
                            if not filecmp.cmp(to_keep, f):
                                print('%s not equal to chosen file')
                                continue
                            print('auto deleting %s: '%f)
                            if not args.dryrun:
                                os.remove(f)
                else:
                    while userinput not in list(range(len(files))):
                        try:
                            userinput = input("enter numer of file you want to keep (s to skip): ")
                            if userinput == 's':
                                break
                            userinput = int(userinput)
                        except ValueError as e:
                            print("enter value between 0 and %s"%len(files))
                    if userinput == 's':
                        continue
                    for i, f in enumerate(files):
                        if i != userinput:
                            print('deleting %s'%f)
                            if not args.dryrun:
                                os.remove(f)



