#!/usr/bin/env python


import os
import argparse
import sys
import re
from platform import system


__author__ = 'Jake Miller'
__date__ = '20180508'
__version__ = '0.02'
__description__ = ''' Recurses through directories searching for file names
                      or strings within files that could be interesting from
                      a security perspective. '''


def interesting_filename_list():
    """Returns a list of string to help determine files of interest.
    """
    interesting_filenames = [
        'pass', 'cred', 'user', '.conf', 'ssh', '.ssh', 'key', 'git', 
        '.xml', '.properties', '.ear', '.war'
    ]
    return interesting_filenames 


def interesting_strings_list():
    """ Returns a list of strings to help determine strings of interest.
    """
    interesting_strings = [
        'pass', 'pwd', 'hash', 'cred', 'user', 'key', '<value>'
    ]
    return interesting_strings 


def has_interesting_content(filepath):
    """Reads the contents of a file and see if interesting strings are 
    present.

    Returns the filename where the string was located along with data around
    the string for context.
    """
    interesting_strings = interesting_strings_list()
    try:
        if sys.version.startswith('3'):
            with open(filepath, encoding='utf-8', errors='replace') as fh:
                contents = fh.read()
        else:
            with open(filepath) as fh:
                contents = fh.read()
    except Exception as e:
        if args.verbose:
            print('Error on {}: {}'.format(filepath, e))
        return
    context = []
    for string in interesting_strings:
        regex = "(?:(?i)" + string + ").{1,60}"
        matches = (re.findall(regex, contents))
        context += [item for item in matches]
    return context


def is_interesting_filename(filename):
    """Returns the name of the file if it has an intersting name, otherwise
    returns None.
    """
    interesting_filenames = interesting_filename_list()
    for string in interesting_filenames:
        if string in filename:
            return True
        else:
            continue


def main():
    """Searches files from a specified file listing, or recurses the
    filesystem to look for interesting file names or strings within
    the files.
    """
    # Lots of repeat code. Need to fix.

    # Reads files from a file list and perfroms searches
    if args.file_list:
        filenames = open(args.file_list).read().splitlines()
        for filename in filenames:

            if args.search_filenames:
                is_interesting = is_interesting_filename(filename)
                if is_interesting:
                    print(filename)

            if args.search_contents:
                interesting_content = has_interesting_content(filename)
                if interesting_content:
                    if not args.search_filenames:
                        print(filename)
                    for item in interesting_content:
                        print("    " + item)

            if args.write_to_file:
                if args.search_contents:
                    if interesting_content:
                        outfile.write(filename + "\n")
                        for item in interesting_content:
                            outfile.write("    " + item + "\n")
                else:
                    outfile.write(filename + "\n")

    # Traverses the filesystem and conducts searches
    else:
        for root, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:

                if args.search_filenames:
                    is_interesting = is_interesting_filename(filename)
                    if is_interesting:
                        print(os.path.join(root, filename))

                if args.search_contents:
                    interesting_content = has_interesting_content(os.path.join(root, filename))
                    if interesting_content:
                        if not args.search_filenames:
                            print(os.path.join(root, filename))
                        for item in interesting_content:
                            print("    " + item)

                if args.write_to_file:
                    if args.search_contents:
                        if interesting_content:
                            outfile.write(os.path.join(root, filename) + "\n")
                            for item in interesting_content:
                                outfile.write("    " + item + "\n")
                    else:
                        outfile.write(os.path.join(root, filename) + "\n")



if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-sc", "--search_contents", help="search only the contents of files for interesting strings", action="store_true")
    parser.add_argument("-sf", "--search_filenames", help="search only the filenames only for interesting strings", action="store_true")
    parser.add_argument("-d", "--directory", nargs='?', const='./', help="specify the directory to begin searching")
    parser.add_argument("-w", "--write_to_file", nargs='?', const='file_searcher_output', help="writes output to a file")
    parser.add_argument("-fl","--file_list", help="Read a list of filenames to perform the search.")
    args = parser.parse_args()

    if not(args.search_filenames or args.search_contents):
        parser.print_help()
        print("\n[-] Please specify whether to search the file names (-sf), contents (-sc), or both (-sf -sc.\n")
        exit()

    if args.file_list:
        if not os.path.exists(args.file_list):
            parser.print_help()
            print("\n[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
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
        if sys.version.startswith('3'):
            outfile = open(args.write_to_file, 'a', encoding='utf-8', errors='replace')
        else:
            outfile = open(args.write_to_file, 'a')
    
    main()