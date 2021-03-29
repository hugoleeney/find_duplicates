import os


def uwalk(top, topdown=True, onerror=None, followlinks=False, start_at=None,
        dont_explore_names=[], dont_explore_paths=[]):
    """
    Same function as os.walk but with extra features.
    start_at: don't yield any files until this directory path is reached
    dont_explore_names: don't yield any files with these names
    dont_explore_paths: don't yield any files in this sub-directory
    """

    process = True
    if start_at:
        process = False

    top = os.fspath(top)
    dirs = []
    nondirs = []
    walk_dirs = []

    try:
        scandir_it = os.scandir(top)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    with scandir_it:
        while True:
            try:
                try:
                    entry = next(scandir_it)
                except StopIteration:
                    break
            except OSError as error:
                if onerror is not None:
                    onerror(error)
                return

            try:
                is_dir = entry.is_dir()
            except OSError:
                is_dir = False

            if is_dir:
                dirs.append(entry.name)
            else:
                nondirs.append(entry.name)

            if not topdown and is_dir:
                if followlinks:
                    walk_into = True
                else:
                    try:
                        is_symlink = entry.is_symlink()
                    except OSError:
                        is_symlink = False
                    walk_into = not is_symlink

                if walk_into and entry.name not in dont_explore_names and \
                        entry.path not in dont_explore_paths:
                    walk_dirs.append(entry.path)

    if topdown:
        if not start_at:
            yield top, dirs, nondirs
        islink, join = os.path.islink, os.path.join
        for dirname in dirs:
            
            new_path = os.path.normpath(os.path.join(top, dirname))
            if start_at and new_path == start_at:
                start_at = None
                process = True

            if not process and start_at and start_at.startswith(new_path):
                process = True

            new_path = join(top, dirname)
            if (followlinks or not islink(new_path))  and \
                    dirname not in dont_explore_names and \
                    os.path.normpath(new_path) not in dont_explore_paths and \
                    process:
                yield from uwalk(new_path, topdown, onerror, followlinks, start_at, dont_explore_names, dont_explore_paths)
            
            if process:
                start_at = None
    else:
        for new_path in walk_dirs:
            
            new_path = os.path.normpath(new_path)
            if start_at and new_path == start_at:
                start_at = None
                process = True
            if not process and start_at and start_at.startswith(new_path):
                process = True

            if os.path.basename(new_path) not in dont_explore_names and \
                    os.path.normpath(new_path) not in dont_explore_paths and \
                    process:
                yield from uwalk(new_path, topdown, onerror, followlinks, start_at, dont_explore_names, dont_explore_paths)
            if process:
                start_at = None

        if not start_at:
            yield top, dirs, nondirs
