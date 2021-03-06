# General Information

- a collection of scripts for finding and deleting duplicate files
- amalgamated under a parent script `fd.py` which can be called with subcommands
- not production ready - use with caution
- developed with Python 3.8.5
    - on Ubuntu WSL2 with pyenv, pyenv-virtualenv
- original use case was removing 500MB of duplicate photos and videos from a 800MB archive

## Installation

Download the entire directory. Run any script similarly to the command below:

```
python <path to location>/finddupes.py -h
```

or

```
python <path to location>/fd.py subcommand -h
```

`fd.py` is compatible with `pyinstaller`. To build a binary:

```
pyinstaller fd.py --onefile
```


# Which file/sub-command should I use?


## I only want information. I do not want to delete any files.

Use `number_of_dupes.py` to get the number and size of possible duplicates. It can also print out all the duplicates as a list.


## I have 2 seperate directories

e.g.
    
    I have two seperate directory structures `dirA` and `dirB` that have possible duplicates between them. I want to delete all duplicates from `dirB`

In this case `finddupes_in_dir.py` is the best solution. You can use `--d`and `--dir` flags to specify `dirA` and `dirB`.


## I want to only delete duplicates that exist in the same directory

Use `finddupes_in_same_folder.py`. You have the option of recursing into subdirectories but it will never look outside of the current directory for duplicates.


## I want to automatically delete duplicates according to previous choices based on the directories the duplicates were present in

Imagine you have the following directory structure.

```
.
├── test
│   ├── a.txt
│   └── t.txt
├── test2
│   ├── a.txt
│   └── t.txt
```

`finddupes_prompt_by_dir.py` will first prompt you about the duplicates called `a.txt`. 

```
enter 0 to delete ./test/a.txt
enter 1 to delete ./test2/a.txt
your choice (2 to skip):
```

It will remmeber your answer when it comes to `test/t.txt` and `test2/t.txt` assuming they are duplicates too. If you delete `a.txt` from `test2` then `t.txt` from `test2` will automatically be deleted as a duplicate without a prompt.


## I want to be prompted for every file deletion

There are 2 scripts that will do this for you.

* `finddupes.py` - This will prompt you as it goes along always asking you to decide between 2 files.
* `find_all_dupes_then_prompt.py` - This does all the detective work up front and then for each duplication (could be many files all the same) it asks you to choose one file to keep. This is better for having an overall view of duplicate files across directory structures.

TODOs 

## I want to automatically delete duplicates based on ...

- created time - TODO
- modified time - TODO
- length of path -TODO
- length of filename - TODO
- order found - TODO


# General TODO

- allow user to move files to another directory instead of deleting
- allow user to pick many files to keep.
- save a session so that detective work doesn't have to be done again.
    - allow offline session annotation to delete files


# Empty Directories

Once you are finished deleting dupes you might be left with a number of empty directories. There are suitable system
commands for finding and deleting these.

```
find ./ -type d -empty

find ./ -type d -empty -delete
```
