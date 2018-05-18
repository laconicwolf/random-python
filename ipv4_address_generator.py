import itertools
import sys
import re
if sys.version.startswith('3'):
    import ipaddress


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180407'
__version__ = '0.01'
__description__ = ''' Accepts an IP address range and prints IP 
                  addresses to the terminal.  
                  '''


def ip_range(input_string):
    ''' Accepts a dash specified range and returns a list of ip addresses
    within that range. Adapted from:
    https://stackoverflow.com/questions/20525330/python-generate-a-list-of-ip-addresses-from-user-input
    ''' 
    octets = input_string.split('.')
    chunks = [list(map(int, octet.split('-'))) for octet in octets]
    ranges = [range(c[0], c[1] + 1) if len(list(c)) == 2 else c for c in chunks]
    addrs = ['.'.join(list(map(str, address))) for address in itertools.product(*ranges)]
    return addrs


def cidr_ip_range(input_string):
    ''' Accepts a CIDR range and returns a list of ip addresses
    within the CIDR range.
    '''
    addr_obj = ipaddress.ip_network(input_string)
    addrs = [addr for addr in addr_obj.hosts()]
    return addrs


def usage():
    ''' Returns usage message and examples to terminal.
    '''
    message = '\n[*] Usage:   ./ip_generator.py <address range>\n'
    message += '[*] Example: ./ip_generator.py 192.168.0-1.20-30\n'
    if sys.version.startswith('3'):
        message += '[*] Example: ./ip_generator.py 192.168.0.0/24\n'
    return message


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(usage())
        exit()

    my_range = sys.argv[1]

    if not '-' in my_range and not '/' in my_range:
        if sys.version.startswith('3'):
            print(usage())
            print("[-] Please either specify a CIDR range or an octet range with a dash ('-').")
            exit()
        else:
            print(usage())
            print("[-] Please specify an octet range with a dash ('-').")
            exit()

    # https://www.regextester.com/93987
    cidr_regex = r'^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$'
    
    # adapted from https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex
    dash_regex = r'^[\d+-?]{1,7}\.[\d+-?]{1,7}\.[\d+-?]{1,7}\.[\d+-?]{1,7}$'

    if '-' in my_range:
        if '/' in my_range:
            if sys.version.startswith('3'):
                print(usage())
                print("[-] Please either use CIDR notation or specify octet range with a dash ('-'), not both.")
                exit()
            else:
                print(usage())
                print("[-] CIDR notation not supported with Python2. For CIDR notation, please use Python3.")
                exit()
        if not re.findall(dash_regex, my_range):
            print(usage())
            print('[-] Invalid IP range detected. Please try again.')
            exit()
        addresses = ip_range(my_range)

    elif '/' in my_range:
        if sys.version.startswith('2'):
            print(usage())
            print("[-] CIDR notation not supported when runnng this script with Python2. For CIDR notation, please use Python3.")
            exit()
        try:
            if not re.findall(cidr_regex, my_range):
                print(usage())
                print('[-] Invalid CIDR range detected. Please try again.')
                exit()
            addresses = cidr_ip_range(my_range)
        except ValueError as error:
            print(usage())
            print('[-] Invalid CIDR range detected. Please try again.')
            print('[-] {}'.format(error))
            exit()
    
    for address in addresses:    
        # additional validation to dump any octet larger than 255
        octets = str(address).split('.')
        invalid_addr = [octet for octet in octets if int(octet) > 255]
        if invalid_addr:
            continue 
        print(address)
