#!/usr/bin/env python3

__author__ = "Jake Miller (@LaconicWolf)"
__date__ = "20181126"
__version__ = "0.01"
__description__ = """SSHs into a Kali instance and starts Responder.py."""

import os
import sys
import argparse

# Third party modules
missing_modules = []
try:
    import paramiko
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    missing_modules.append(missing_module)

if missing_modules:
    for m in missing_modules:
        print('[-] Missing module: {}'.format(m))
        print('[*] Try running "pip3 install {}", or do an Internet search for installation instructions.\n'.format(m.strip("'")))
    exit()

def ssh_connect(hostname, username, key_filename, port):
    """Attempts to connect to a server with the specified parameters.
    Returns an ssh client instance.
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(hostname=hostname,
                           username=username,
                           port=port,
                           key_filename=key_filename)
        print('[+] Authentication successful on {}:{}'.format(hostname, str(port)))
    except paramiko.ssh_exception.NoValidConnectionsError:
        print('[-] Unable to connect via SSH to {}:{}'.format(hostname, port))
        exit()
    except paramiko.ssh_exception.AuthenticationException:
        print('[-] Authentication failed on {}:{}'.format(hostname, port))
        exit()
    except Exception as e:
        print('[-] An unknown error occurred on {}:{}.\nError: {}'.format(hostname, port, e))
        exit()
    return ssh_client

def start_responder(ssh_client):
    """Starts responder."""
    print('[*] Starting Responder...')
    stdin, stdout, stderr = ssh_client.exec_command('sudo responder -I eth0 -bf')

def get_results(ssh_client):
    """Reads and returns the responder log results"""
    print('[*] Checking for results...')
    stdin, stdout, stderr = ssh_client.exec_command('ls /usr/share/responder/logs/')
    files = stdout.read().decode().split()
    for file in files:
        if file.startswith('HTTP-Basic'):
            stdin, stdout, stderr = ssh_client.exec_command('cat /usr/share/responder/logs/{}'.format(file))
            output = stdout.read().decode().split()
            for line in output:
                print(line)

def main():
    client = ssh_connect(host, user, key_file, port)
    if args.start_responder:
        start_responder(client)
    if args.get_results:
        get_results(client)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity",
                        action="store_true")
    parser.add_argument("-s", "--start_responder",
                        help="SSHs into the server and starts responder",
                        action="store_true")
    parser.add_argument("-g", "--get_results",
                        help="SSHs into the server and gets the responder results",
                        action="store_true")
    parser.add_argument("-a", "--address",
                        help="Specify the IP address or hostname to SSH into.")
    parser.add_argument("-k", "--key_file",
                        help="Specify the SSH key file to use")
    parser.add_argument("-u", "--username",
                        help="Specify the SSH username")
    parser.add_argument("--port",
                        nargs='?',
                        const=22,
                        default=22,
                        type=int,
                        help="Specify the SSH port. Default is 22")
    args = parser.parse_args()

    if not args.address:
        parser.print_help()
        print('\n[-] Please specify an IP address or hostname to SSH into.\n')
        exit()
    if not args.username:
        parser.print_help()
        print('\n[-] Please specify the SSH username.\n')
        exit()
    if not args.key_file:
        parser.print_help()
        print('\n[-] Please specify the path to the SSH keyfile.\n')
        exit()
    if not args.start_responder and not args.get_results:
        parser.print_help()
        print('\n[-] Please either specify to start responder (-s) or to get the results (-g).\n')
        exit()

    host = args.address
    user = args.username
    key_file = args.key_file
    port = args.port
    main()    
