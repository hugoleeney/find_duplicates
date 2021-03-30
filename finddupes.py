import os
import argparse
import filecmp

from uwalk import uwalk


def main(args):
    
    if not args.dryrun and not force:
        user_continue = input("WARNING this is not a dry run. Any dupes found will be deleted. Enter '1' to quit now.")
        if user_continue == '1':
            exit()
    else:
        print("DRY RUN")
        
    found = {}

    for path in args.d:
        for dirpath, dirnames, files in uwalk(path, 
                start_at=args.start_at,
                dont_explore_names=args.dont_explore_names, 
                dont_explore_paths=args.dont_explore_paths):
            for name in files:
                filepath = os.path.join(dirpath, name)
                size = os.path.getsize(filepath)
                criteria = size
                if not args.ignore_zero_size or size != 0:
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
                        found[criteria] = os.path.join(dirpath, name)


if __name__ == "__main__":
    
    description = """
    Search provided directories looking for dupes. Match first on size, confirm with
    a full file comparison. Prompt user to choose one file or the other.
    """
    parser = argparse.ArgumentParser(description=description )
    parser.add_argument('--d', required=True, action="append", help="directory where to look for dupes")
    parser.add_argument('--dryrun', action='store_true', help="go through the motions but don't delete anything")
    parser.add_argument('--force', action='store_true', help="if not a dry run don't prompt")
    parser.add_argument('-n', '--dont_explore_names', action='append', help='directory names not to explore e.g. .git', default=[])
    parser.add_argument('-p', '--dont_explore_paths', action='append', help='directory paths not to explore e.g. .git', default=[])
    parser.add_argument('-i', '--ignore_zero_size', action='store_true', help='ignore any file with zero size')
    parser.add_argument('-s', '--start_at', help="a directory where to start looking, if not found no files will be processed (n.b --dont_explore_paths)", default=None)
    args = parser.parse_args()

    main(args)
