import os
import argparse
import filecmp


description = """
Search provided directories looking for dupes. Match first on size, confirm with
a full file comparison. Prompt user to choose one file or the other.
"""
parser = argparse.ArgumentParser(description=descriptionn )
parser.add_argument('--d', required=True, action="append")
parser.add_argument('--dryrun', action='store_true')
parser.add_argument('--force', action='store_true')
args = parser.parse_args()


if not args.dryrun and not force:
    user_continue = input("WARNING this is not a dry run. Any dupes found will be deleted. Enter '1' to quit now.")
    if user_continue == '1':
        exit()


found = {}

for path in args.d:
    for dirpath, dirnames, files in os.walk(path):
        for name in files:
            filepath = os.path.join(dirpath, name)
            size = os.path.getsize(filepath)
            criteria = (size, t, ext)
            if criteria in found:
                if filecmp.cmp(found[criteria], os.path.join(dirpath, name)):
                    print(0, found[criteria])
                    print(1, filepath)
                    userinput = ''
                    while userinput not in ['0', '1', '2']:
                        userinput = input("enter the number of the file you want to delete (2 to skip): ")
                    if userinput == '2':
                        continue
                    else:
                        to_delete = found[criteria] if userinput == '0' else filepath
                        print('deleting %s' % to_delete)
                        if not args.dryrun:
                            try:
                                os.remove(filepath)
                            except EnvironmentError as e:
                                print("couln't delete file %s" % filepath)
                        else:
                            print('dry run')
                else:
                    print('file contents not the same. Aborting delete')
            else:
                found[criteria] = os.path.join(dirpath, name)

