#!/usr/bin/env python3


__author__ = "Jake Miller (@LaconicWolf)"
__date__ = "20190807"
__version__ = "0.01"
__description__ = """A script that can help search Confluence and output results to a CSV file."""


import sys

if not sys.version.startswith('3'):
    print('\n[-] This script will only work with Python3. Sorry!\n')
    exit()

import argparse
import random
import time
import csv
import os
from base64 import b64encode

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def parse_to_csv(data, csv_name):
    """Given a list of data, adds the items to (or creates) a CSV file."""
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = [
            'Title', 'Link Type', 'URL', 'Media Type', 
            'File Size', 'Comments',
        ]
        csv_writer.writerow(top_row)
        print('[+] The file {} does not exist. New file created!'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError as e:
            print("[-] Permission denied to open the file {}. "
                  "Check if the file is open and try again.".format(csv_name))
            print("Printing data to the terminal:")
            time.sleep(3)
            for item in data:
                print(''.join(str(item)))
            exit()
        csv_writer = csv.writer(csv_file)
        print('[+] {} exists. Appending to file!'.format(csv_name))
    for item in data:
        csv_writer.writerow(item)
    csv_file.close()        


def get_random_useragent():
    """Returns a randomly chosen User-Agent string."""
    win_edge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    win_firefox = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/43.0'
    win_chrome = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
    lin_firefox = 'Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/42.0'
    mac_chrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36'
    ie = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'
    ua_dict = {
        1: win_edge,
        2: win_firefox,
        3: win_chrome,
        4: lin_firefox,
        5: mac_chrome,
        6: ie
    }
    rand_num = random.randrange(1, (len(ua_dict) + 1))
    return ua_dict[rand_num]


def build_request():
    """Implements optional HTTP headers and returns a session object"""
    s = requests.Session()
    if args.proxy:
        s.proxies['http'] = args.proxy
        s.proxies['https'] = args.proxy
    user_agent = args.useragent if args.useragent else get_random_useragent()
    s.headers['User-Agent'] = user_agent
    if args.referer:
        s.headers['Referer'] = args.referer
    if auth:
        s.headers["Authorization"] = "Basic {}".format(auth)
    if args.cookies:
        for key in cookie_dict:
            s.cookies[key] = cookie_dict[key]
    if args.custom_header:
        for header in custom_headers:
            try:
                header_name = header.split(':')[0]
                header_value = ''.join(header.split(':')[1:]).lstrip()
            except Exception as e:
                print('[-] An error occurred while parsing the custom headers: {}'.format(e))
            s.headers[header_name] = header_value
    return s


def make_request(session, url):
    """Makes a web request with a given session object to a 
    specified URL and returns the response.
    """
    try:
        resp = session.get(url, verify=False)
    except Exception as e:
        print('[-] An error occurred: {}'.format(e))
        sys.exit()
    try:
        results = resp.json()
    except Exception as e:
        print('[-] An error occurred while parsing the HTTP response: {}'.format(e))
        sys.exit()
    return results


def parse_search_results(search_results):
    """Parses the search results from a Confluence CQL search query. 
    Returns a tuple of results.
    """
    # dict_keys(['id', 'type', 'status', 'title', 'body', 'metadata', 'extensions', '_links', '_expandable'])
    result_title = search_results.get('title')
    result_type = search_results.get('type')
    extensions = search_results.get('extensions')
    if extensions:
        doctype = extensions.get('mediaType', '')
        filesize = extensions.get('fileSize', '')
        comment = extensions.get('comment', '')
    else:
        doctype = ''
        filesize = ''
        comment = ''
    links = search_results.get('_links')
    display_link = "{}{}".format(base_url, links.get('webui', ''))
    search_data = (result_title, result_type, display_link, doctype, filesize, comment)
    return search_data


def parse_cookies(cookies):
    """Takes a string of cookies and returns a dictionary of cookies 
    to be used in a requests session object.
    """
    cookie_dictionary = {}
    for cookie in cookies:
        all_cookies = cookie.split(';')
        for c in all_cookies:
            c_name = c.lstrip().split('=')[0]
            c_value = ''.join(c.split('=')[1:])
            cookie_dictionary[c_name] = c_value
    return cookie_dictionary


def main():

    # Iterate through the supplied search words
    for term in search_terms:
        url = "{}/rest/api/content/search?cql=text~\"{}\"&expand=body.storage&limit=1000".format(base_url, term)
        
        # Creates and makes an HTTP request. The response var is a JSON 
        # dictionary object, where 'results' is the key value pair of interest.
        # The value of 'results' is a list of dictionaries.
        s = build_request()
        response = make_request(s, url)
        results = response.get('results')

        # Iterate and parse each dictionary. The var 'item_data' contains
        # a tuple of parsed information that is appended to the shared 
        # var 'data' list.
        for results_dictionary in results:
            item_data = parse_search_results(results_dictionary)
            if args.verbose:
                print(item_data)
            data.append(item_data)

    # The shared var 'data' list is parsed to a CSV.
    if args.csv_name:
        parse_to_csv(data, csv_name)
    else:
        parse_to_csv(data, "{}_results-{}.csv".format(sys.argv[0][:-3], str(time.time()).replace('.', '')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--search_query",
        nargs='+',
        help='Specify the string(s) to search for.'
    )
    parser.add_argument(
        "-f", "--file_query",
        help="Specify a file of strings to search for."
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Increase output verbosity",
        action="store_true"
    )
    parser.add_argument(
        "-pr", "--proxy", 
        help="Specify a proxy to use (-pr 127.0.0.1:8080)"
    )
    parser.add_argument(
        "-ch", "--custom_header", 
        nargs='*',
        help='Specify one or more custom header and value delimited. Example: -ch "X-Custom-Header: CustomValue"'
    )
    parser.add_argument(
        "-a", "--auth",
        help='Specify a username and password delimited with ":" for basic authentication. Example: -a myuser:mypassword.'
    )
    parser.add_argument(
        "-c", "--cookies",
        nargs="*",
        help='Specify cookie(s). Example: -c "C1=IlV0ZXh0L2h; C2=AHWqTUmF8I;"'
    )
    parser.add_argument(
        "-ua", "--useragent", 
        help="Specify a User Agent string to use. Default is a random User Agent string."
    )
    parser.add_argument(
        "-r", "--referer", 
        help="Specify a referer string to use."
    )
    parser.add_argument(
        "-u", "--url",
        help="Specify a single url formatted http(s)://addr:port."
    )
    parser.add_argument(
        "-csv", "--csv_name",
        help="Specify a name for the csv file. Default is {}_results<timestamp>.csv".format(sys.argv[0][:-3])
    )

    # Might add these options eventually
    '''parser.add_argument(
        "-t", "--threads",
        nargs="?",
        type=int,
        const=10,
        default=10,
        help="specify number of threads (default=10)"
    )
    parser.add_argument(
        "-to", "--timeout",
        nargs="?", 
        type=int, 
        default=10, 
        help="specify number of seconds until a connection timeout (default=10)"
    )'''
    args = parser.parse_args()

    # Suppress SSL warnings in the terminal
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if not args.search_query and not args.file_query:
        print('[-] Please specify strings to search for (-s word1 word2) or specify the ',
              'path to a file containing strings to search for (-f /path/to/file.txt)')
        exit()
    search_terms = ''
    if args.search_query:
        search_terms = args.search_query
    if args.file_query:
        if not os.path.exists(args.file_query):
            print("\n[-] The file {} cannot be found or you do not have permission to open ",
                  "the file. Please check the path and try again\n".format(args.file_query))
            exit()
        with open(args.file_query) as fh:
            search_terms = fh.read().splitlines()

    if not args.url:
        print('[-] Please specify the Confluence URL you\'d like to query (-u https://my.confluence.com:8443.')
        exit()
    base_url = args.url.strip('/')
    if args.auth:
        if ':' not in args.auth:
            print('[-] The authentication credentials must be formatted username:password ',
                  'delimited with a ":".')
            exit()
        auth = b64encode(args.auth.encode()).decode()
    else:
        auth = ''

    if args.cookies:
        cookie_dict = parse_cookies(args.cookies)

    exit = 0
    if args.custom_header:
        for header in args.custom_header:
            if ":" not in header:
                print('[-] Custom headers must be delimited with a ":". Example: ',
                      '-ch "custheader1: avalue" "custheader2: anothervalue')
                exit = 1
        custom_headers = args.custom_header
    if exit: exit()

    csv_name = ''
    if args.csv_name:
        csv_name = args.csv_name.rstrip('.csv') + '.csv'
        
    # Shared list that will hold the data for all searches
    data = []
    
    # Print banner and arguments
    print()
    word_banner = '{} version: {}. Coded by: {}'.format(sys.argv[0].title()[:-3], __version__, __author__)
    print('=' * len(word_banner))
    print(word_banner)
    print('=' * len(word_banner))
    print()
    for arg in vars(args):
        if getattr(args, arg):
            if arg == 'auth':
                continue
            print('{}: {}'.format(arg.title().replace('_',' '), getattr(args, arg)))
    print()
    time.sleep(3)

    main()
