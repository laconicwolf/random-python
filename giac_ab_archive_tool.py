try:
    import requests
except ImportError:
    print('\n[*] This script requires the requests module')
    print("[*] Please 'pip install requests', and try running the script again.")
    exit()
import argparse
import re
import getpass
import os
import sys
import platform
from time import sleep


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180309'
__version__ = '0.01'
__description__ = ''' A simple tool to download and search the GIAC 
                      advisory board archives '''


if not sys.version.startswith('3'):
    print('\nThis script is intended to be run with Python3.')
    print('The output may not look right in other versions.')
    print('If using another version and encounter an error, try using Python3\n')
    sleep(3.5)


def authenticate(username, password):
    """ Authenticates to the SANS advisory board archives and authenticates
    """
    s = requests.Session()
    data = {'username': username,
            'password': password,
            'submit': "Let+me+in..."}
    resp = s.post(url, data)
    if 'Authorization\nfailed.' in resp.text:
        print('[-] Authentication failed! Verify your credentials and try again.')
        print('Exiting!')
        exit()

    return s, resp.text


def test_connection():
    """ Attempts to connect to the target URL
    """
    try:
        requests.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Received the following error:\n\n    {}'.format(url, e))
        exit()


def make_directory(dirname):
    """ Create a directory to store downloaded archive files
    """
    os.mkdir(dirname)


def inventory_current_files(dirname):
    """ Returns a list of files in the specified directory
    """
    current_files = os.listdir(dirname)
    return current_files


def download_text_file(session, file, destination):
    """ Downloads a specifed file. Returns the local filename
    """
    
    local_filename = destination + sep + file
    file_url = url.strip('/') + '/' + file
    if args.verbose:
        print('[*] Downloading {}...'.format(file_url))
    resp = session.get(file_url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename


def parse_webpage(text):
    """ Scrapes everything in quotes that contain '.txt'. Returns
    a list of these items to be downloaded.
    """
    text_file_list = re.findall(r'\"(.+txt)\"', text)
    return text_file_list


def parse_subjects(filepaths):
    """ Reads a list of filepaths, opens each file, and parses the 
    subject line. Returns a dictionary of filenames as keys and list
    of subject lines as values.
    """
    subject_dict = {}
    for filepath in filepaths:
        filename = filepath.split(sep)[-1]
        with open(filepath) as fh:
            text = fh.read()
        subjects = re.findall(r'Subject: \[giac-alumni\] (.*)', text)
        subjects += re.findall(r'Subject: \[advisory-board-open\] (.*)', text)
        subjects = set(subjects)
        subject_dict[filename] = subjects
    return subject_dict


def read_files(filepaths):
    """ Reads a list of filepaths and opens/reads each file. 
    Returns a dictionary of filenames as keys with the text 
    as values.
    """
    full_text_dict = {}
    for filepath in filepaths:
        filename = filepath.split(sep)[-1]
        with open(filepath) as fh:
            text = fh.read()
        full_text_dict[filename] = text
    return full_text_dict


def main():
    if args.download_archives:
        if args.verbose:
            print('[*] Testing connection...')
        test_connection()
        if args.verbose:
            print('[*] Authenticating...')
        session, page_text  = authenticate(username, password)

        # scrapes the archives for hrefs ending with .txt
        web_file_list = parse_webpage(page_text)
        if not os.path.exists(dirname):
            if args.verbose:
                print('[*] Creating directory to store archived threads')
            make_directory(dirname)
        current_files = inventory_current_files(dirname)
        
        # downloads files that are on the site but not in the directory
        for file in web_file_list:
            if file not in current_files:
                print("Downloading {}".format(file))
                file_written = download_text_file(session, file, dirname)
                if args.verbose:
                    print('[+] {} download to {}'.format(file, file_written))

    if args.search_archives:
        if not os.path.exists(dirname):
            print('[-] Cannot find folder GIAC_AB_Archives in the current directory.')
            print('    Use the -d option to download the archives first, then use -s')
            print('    to search')
            exit()
        current_files = inventory_current_files(dirname)
        if not current_files:
            print('[-] No files exist in the GIAC_AB_Archives folder. Use the')
            print('    -d option to download the archives first, then use -s')
            print('    to search')
            exit()
        if args.search_subject:
            filepaths = [dirname + sep + filename for filename in current_files]
            subjects = parse_subjects(filepaths)
            for word in search_words:
                for key, value  in subjects.items():
                    for item in value:
                        if word in item:
                            print(key, item)
        if args.search_full_text:
            filepaths = [dirname + sep + filename for filename in current_files]
            texts = read_files(filepaths)
            for word in search_words:
                for key, value  in texts.items():
                    regex = ".{20}"+ word + ".{45}"
                    matches = re.findall(regex, value)
                    if matches:
                        all_occurrences = [key + ' ' + match for match in matches]
                        all_occurrences = set(all_occurrences)
                        for occurence in all_occurrences:
                            file = occurence.split()[0]
                            contents = occurence.split()[1:]
                            contents = ' '.join(contents)
                            print(file + '  ...' + contents + '...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--download_archives", help="download the advisory board text files", action="store_true")
    parser.add_argument("-p", "--password", help="your GIAC password to access the AB archives")
    parser.add_argument("-u", "--username", help="your username/email address for the GIAC AB archives")
    parser.add_argument("-s", "--search_archives", help="search the advisory board local text files", action="store_true")
    parser.add_argument("-ss", "--search_subject", nargs='*', help="search for word(s) in the subject line and return the files with that contain that word.(s)")
    parser.add_argument("-sf", "--search_full_text", nargs='*', help="search for word(s) in the file and return the file name and partial sentence for context")
    args = parser.parse_args()

    # determines the file path seperator
    if platform.system() == 'Windows':
        sep = '\\'
    else:
        sep = '/'

    if args.download_archives and args.search_archives:
        parser.print_help()
        print('\n[-] Please choose only -s to search the local archive files or -d to download the archives. Not both.\n')
        exit()

    if not args.download_archives and not args.search_archives:
        parser.print_help()
        print('\n[-] Please use the -s option to search the local archive files or -d to download the archives\n')
        exit()

    if args.search_archives and not (args.search_full_text or args.search_subject):
        parser.print_help()
        print('\n[-] Please add either the -ss (search subject line) or -sf (search full text) option.\n')
        exit()

    if args.search_subject and args.search_full_text:
        parser.print_help()
        print('\n[-] Please choose only -ss or -sf option, not both.\n')
        exit()

    if args.search_subject:
        search_words = args.search_subject

    if args.search_full_text:
        search_words = args.search_full_text

    username = args.username
    password = args.password

    if args.download_archives:
        try:
            input = raw_input
        except:
            pass

        if not args.username:
            username = input('\nPlease enter your username:\n')

        if not args.password:
            password = getpass.getpass('Please enter your password:\n')
    
    dirname = 'GIAC_AB_Archives'
    url = "https://lists.sans.org/mailman/private/advisory-board-open/"

    main()