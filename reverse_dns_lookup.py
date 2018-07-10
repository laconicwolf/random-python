#!/usr/bin/env python3

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180710'
__version__ = '0.01'
__description__ = """Attempts reverse DNS lookups of a specified IP range."""


import string
import itertools
import sys
import re
import argparse
if sys.version.startswith('3'):
    import ipaddress

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('[*] Try running "pip install requests", or do an Internet search for installation instructions.')
    exit()

try:
    import dns.resolver, dns.reversename, dns.query, dns.zone
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('[*] Try running "pip install dnspython", or do an Internet search for installation instructions.')
    exit()


def ip_range(input_string):
    """Accepts a dash specified range and returns a list of ip addresses
    within that range. Adapted from:
    https://stackoverflow.com/questions/20525330/python-generate-a-list-of-ip-addresses-from-user-input
    """
    octets = input_string.split('.')
    chunks = [list(map(int, octet.split('-'))) for octet in octets]
    ranges = [range(c[0], c[1] + 1) if len(list(c)) == 2 else c for c in chunks]
    addrs = ['.'.join(list(map(str, address))) for address in itertools.product(*ranges)]
    return addrs


def cidr_ip_range(input_string):
    """Accepts a CIDR range and returns a list of ip addresses
    within the CIDR range.
    """
    addr_obj = ipaddress.ip_network(input_string)
    addrs = [addr for addr in addr_obj.hosts()]
    return addrs


def ptr_lookup(address):
    """Performs a reverse DNS lookup and returns the result."""
    addr = dns.reversename.from_address(address)
    try:
        resolved_name = str(dns.resolver.query(addr, "PTR")[0])
    except Exception as e:
        if args.verbose:
            print(e)
        return
    return resolved_name


def main():
    results = [((ptr_lookup(str(address)), address)) for address in ip_addresses]
    print('\n{:35}{:35}'.format("DOMAIN NAME", "IP ADDRESS"))
    for item in results:
        domain_name = item[0]
        ip_address = item[1]
        if domain_name is not None:
            if args.domain:
                if args.domain not in domain_name:
                    continue 
            print('{:35}{:35}'.format(domain_name.strip('.'), ip_address))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")
    parser.add_argument("-r", "--range",
                        help="Specify the IP range to test. Example: ./{0} -r 192.168.0.0/24 or ./{0} -r 192.168.0.0-255".format(sys.argv[0]))
    parser.add_argument("-d", "--domain",
                        help="Limit results to those that contain the specified domain.")
    parser.add_argument("-f", "--file",
                        help="Specify file containing IP addresses to resolve.")
    parser.add_argument("-a", "--address",
                        help="Specify a single IP address to resolve.")
    args = parser.parse_args()
    if not args.file and not args.range and not args.address:
        parser.print_help()
        print()
        print('[-] Please specify IP addresses to resolve.')
        print('[*] Example: ./{} -r 192.168.0.0/24'.format(sys.argv[0]))
        print('[*] Example: ./{} -f /path/to/addr_file'.format(sys.argv[0]))
        print('[*] Example: ./{} -a 192.168.0.1'.format(sys.argv[0]))
        print()
        exit()

    if args.address:
        if '/' in args.address or '-' in args.address or string.ascii_letters in args.address:
            print('\n[-] Invalid characters detected in IP address.\n')
            exit()
        ip_addrs = [args.address]
    if args.file:
        if not os.path.exists(args.file):
            parser.print_help()
            print("\n[-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        ip_addrs = open(args.file).read().splitlines()
        for ip in ip_addrs:
            if '/' in ip or '-' in ip or string.ascii_letters in ip:
                print('\n[-] Invalid characters detected in IP address in file. Please \
                    inspect the contents of the file and try again.\n')
                exit()
    if args.range:
        if not '-' in args.range and not '/' in args.range:
            if sys.version.startswith('3'):
                parser.print_help()
                print("\n[-] Please either specify a CIDR range or an octet range with a dash ('-').\n")
                exit()
            else:
                parser.print_help()
                print("\n[-] Please specify an octet range with a dash ('-').\n")
                exit()

        # https://www.regextester.com/93987
        cidr_regex = r'^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$'
        
        # adapted from https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex
        dash_regex = r'^[\d+-?]{1,7}\.[\d+-?]{1,7}\.[\d+-?]{1,7}\.[\d+-?]{1,7}$'

        if '-' in args.range:
            if '/' in args.range:
                if sys.version.startswith('3'):
                    parser.print_help()
                    print("\n[-] Please either use CIDR notation or specify octet range with a dash ('-'), not both.\n")
                    exit()
                else:
                    parser.print_help()
                    print("\n[-] CIDR notation not supported with Python2. For CIDR notation, please use Python3.\n")
                    exit()
            if not re.findall(dash_regex, args.range):
                parser.print_help()
                print('\n[-] Invalid IP range detected. Please try again.\n')
                exit()
            ip_addrs = ip_range(args.range)

        elif '/' in args.range:
            if sys.version.startswith('2'):
                parser.print_help()
                print("\n[-] CIDR notation not supported when runnng this script with Python2. For CIDR notation, please use Python3.\n")
                exit()
            try:
                if not re.findall(cidr_regex, args.range):
                    parser.print_help()
                    print('\n[-] Invalid CIDR range detected. Please try again.\n')
                    exit()
                ip_addrs = cidr_ip_range(args.range)
            except ValueError as error:
                parser.print_help()
                print('\n[-] Invalid CIDR range detected. Please try again.')
                print('[-] {}\n'.format(error))
                exit()

    # Additional validation to dump any octet larger than 255
    ip_addresses = []
    for addr in ip_addrs:    
        octets = str(addr).split('.')
        invalid_addr = [octet for octet in octets if int(octet) > 255]
        if invalid_addr:
            continue 
        ip_addresses.append(addr)
    main()
