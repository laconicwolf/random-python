#!/usr/bin/env python3


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180713'
__version__ = '0.02'
__description__ = 'A program to discover the FTP service, attempt anonymous login, and list directories.'


import ipaddress
import itertools
import argparse
import ftplib
import os
import csv
import pprint


def ftp_anon_login(ftp_obj):
    """Attempts to anonymously login to an FTP server"""
    login_message = ''
    try:
        login_message = ftp_obj.login()
    except ftplib.all_errors:
        pass
    return login_message


def parse_to_csv(data):
    """Accepts a list and adds the items to (or creates) a CSV file."""
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['URL', 'Header', 'Value', 'Status code', 'Header line text', 'Notes']
        csv_writer.writerow(top_row)
        print('\n[+] The file {} does not exist. New file created!\n'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError:
            print("\n[-] Permission denied to open the file {}. Check if the file is open and try again.\n".format(csv_name))
            exit()
        csv_writer = csv.writer(csv_file)
        print('\n[+]  {} exists. Appending to file!\n'.format(csv_name))
    for line in data:
        csv_writer.writerow(line)
    csv_file.close()


def list_directories(ftp_obj, depth=1):
    """Return a recursive listing of an ftp server contents (starting from
    the current directory). Listing is returned as a recursive dictionary, where each key
    contains a contents of the subdirectory or None if it corresponds to a file. Adapted from:
    https://stackoverflow.com/questions/1854572/traversing-ftp-listing
    """
    if depth >= max_depth:
        return ['depth > {}'.format(max_depth)]
    entries = {}
    for entry in (path for path in ftp_obj.nlst() if path not in ('.', '..')):
        try:
            ftp_obj.cwd(entry)
            entries[entry] = list_directories(ftp_obj, depth + 1)
            ftp_obj.cwd('..')
        except ftplib.error_perm:
            entries[entry] = None
    if entries is {}:
        ftp_obj.cwd('/')
        directories = ftp_obj.nlst()
        for item in directories:
            entries[item] = ''
    return entries


def ip_range(input_string):
    """Accepts a '-' specified ip range and returns a list
    of ip addresses. Adapted to Python3 from:
    https://stackoverflow.com/questions/20525330/python-generate-a-list-of-ip-addresses-from-user-input
    """
    octets = input_string.split('.')
    chunks = [list(map(int, octet.split('-'))) for octet in octets]
    ranges = [range(c[0], c[1] + 1) if len(list(c)) == 2 else c for c in chunks]
    addrs = ['.'.join(list(map(str, address))) for address in itertools.product(*ranges)]
    return addrs


def main():
    data = []
    for addr in addrs:
        host_data = []
        ftp = ftplib.FTP()
        try:
            banner = ftp.connect(addr, port, timeout=5)
            print('[+] {0}:{1} - Connection established'.format(addr, port))
            if args.verbose:
                print('      {}'.format(banner))
        except ftplib.all_errors:
            print('[-] {0}:{1} - Unable to connect'.format(addr, port))
            continue
        if args.anon_login:
            login_message = ftp_anon_login(ftp)
            if login_message != '':
                print('[+] {0}:{1} - Anonyomous login established'.format(addr, port))
                anonymous_login = True
            else:
                print('[-] {0}:{1} - Unable to log in. Permission Error'.format(addr, port))
                anonymous_login = False
        else:
            anonymous_login = False
        if args.list_dir:
            all_dirs = ''
            if anonymous_login is True:
                dirs = list_directories(ftp)
                print('[+] {0}:{1} - Directory Listing:'.format(addr, port))
                all_dirs = pprint.pformat(dirs)
                print(all_dirs)
        else:
            all_dirs = ''
        host_data.extend((addr, port, banner, anonymous_login, all_dirs))
        data.append(host_data)
    if args.csv:
        parse_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")
    parser.add_argument("-r", "--range",
                        help="Specify the network range (10.10.10.0/24 or 10.10.10.20-40).")
    parser.add_argument("-i", "--ipaddress",
                        help="Specify IP address of the FTP server.")
    parser.add_argument("-p", "--port",
                        type=int,
                        nargs="?",
                        default='21',
                        help="Specify a port. Default is 21.")
    parser.add_argument("-f", "--input_filename",
                        help="Specify a file containing the a list of hosts to generate web addresses from.")
    parser.add_argument("-a", "--anon_login",
                        help="Attempt to anonymously login to the FTP server.",
                        action="store_true")
    parser.add_argument("-l", "--list_dir",
                        type=int,
                        nargs='?',
                        const="1",
                        help="Lists directories (one deep) if login is allowed. Specify a number to list further directories."
                        )
    parser.add_argument("-csv", "--csv",
                        nargs='?',
                        const='ftp_results.csv',
                        help="specify the name of a csv file to write to. If the file already exists it will be appended")
    args = parser.parse_args()

    if not args.input_filename and not args.range and not args.ipaddress:
        parser.print_help()
        print("\n[-] Please specify an input file (-f) to parse or an IP range (-r)\n")
        exit()
    if args.input_filename:
        if not os.path.exists(args.input_filename):
            parser.print_help()
            print(
                "\n[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        addrs = open(args.input_filename).read().splitlines()
    if args.range:
        if '-' in args.range:
            if '/' in args.range:
                print("\n[-] Unable to accept a CIDR and '-' specified range.\n")
                exit()
            addrs = ip_range(args.range)
        else:
            try:
                addr_obj = ipaddress.ip_network(args.range)
            except ValueError:
                parser.print_help()
                print('\n[-] Please do not specify host bits. Example: -r 10.1.1.0/24\n')
                exit()
            addrs = [addr for addr in addr_obj.hosts()]
    if args.ipaddress:
        addrs = [args.ipaddress]
    if args.csv:
        csv_name = args.csv

        # Check to see if the file is open. Better to check now then having an error later.
        try:
            csv_file = open(csv_name, 'a', newline='')
            csv_file.close()
        except PermissionError:
            print("\n[-] Permission denied to open the file {}. Check if the file is open and try again.".format(
                csv_name))
            exit()
    
    port = args.port
    max_depth = args.list_dir

    print("\n[+]  Loaded {} FTP server addresses to test\n".format(str(len(addrs))))
    main()
