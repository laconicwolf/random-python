import os
import argparse
from platform import system


__author__ = 'Jake Miller'
__date__ = '20180122'
__version__ = '0.01'
__description__ = ''' Recurses through directories searching for file names
                      or strings within files that could be interesting from
                      a security perspective. '''


def interesting_filename_list():
    ''' Returns a list of string to help determine files of interest.
    '''
    interesting_filenames = [
        'pass', 'cred', 'user', '.conf', 'ssh', '.ssh', 'key', 'git'
    ]

    return interesting_filenames 


def interesting_strings_list():
    ''' Returns a list of strings to help determine strings of interest.
    '''
    interesting_strings = [
        'pass', 'cred', 'user', 'key'
    ]

    return interesting_strings 


def has_interesting_content(filepath):
    ''' Reads the contents of a file and see if interesting strings are 
    present.

    Returns the filename where the string was located along with data around
    the string for context.
    '''
    interesting_strings = interesting_strings_list()
    try:
        with open(filepath, encoding='utf-8', errors='replace') as fh:
            contents = fh.read()
    except (FileNotFoundError, PermissionError) as e:
        if args.verbose:
            print('Error on {}: {}'.format(filepath, e))
        return

    for string in interesting_strings:
        index = contents.find(string)
        if index != -1:
            context = contents[index:index + 20]
            return context
        else:
            continue


def is_interesting_filename(filename):
    ''' Reviews the name of a file to see if it matches an intersting string.
    
    Returns the name of the file if the intersting string is passed, otherwise
    returns None.
    '''
    interesting_filenames = interesting_filename_list()

    for string in interesting_filenames:
        if string in filename:
            return True
        else:
            continue


def main():

    # recurses the file system
    for root, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:

            if args.search_filenames:

                # searches for key words in the filename
                is_interesting = is_interesting_filename(filename)
                if is_interesting:
                    print(os.path.join(root, filename))

            if args.search_contents:

                # searches for key words in file contents
                interesting_content = has_interesting_content(os.path.join(root, filename))
                if interesting_content:
                    if not args.search_filenames:
                        print(os.path.join(root, filename))
                    print(interesting_content)

            if args.write_to_file:

                if args.search_contents:
                    if interesting_content:
                        outfile.write(os.path.join(root, filename) + "," + interesting_content + '\n')
                else:
                    outfile.write(os.path.join(root, filename))



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-sc", "--search_contents", help="search only the contents of files for interesting strings", action="store_true")
    parser.add_argument("-sf", "--search_filenames", help="search only the filenames only for interesting strings", action="store_true")
    parser.add_argument("-d", "--directory", nargs='?', const='./', help="specify the directory to begin searching")
    parser.add_argument("-w", "--write_to_file", nargs='?', const='file_searcher_output', help="writes output to a file")
    args = parser.parse_args()

    if not(args.search_filenames or args.search_contents):
        parser.print_help()
        print("\n [-]  Please specify whether to search the file names (-sf), contents (-sc), or both (-sf -sc.\n")
        exit()

    if args.directory:
        root_dir = args.directory
    else:
        root_dir = './'

    # checks the OS type and sets the filepath seperator
    if system() == 'Windows':
        sep = '\\'
    else:
        sep = '/'

    if args.write_to_file:
        outfile = open(args.write_to_file, 'a', encoding='utf-8', errors='replace')
    
    main()