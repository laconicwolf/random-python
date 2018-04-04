import itertools
import sys
if sys.version.startswith('3'):
    import ipaddress

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
    message = '''\n[*] Usage:   ./ip_generator.py <address range>
[*] Example: ./ip_generator.py 192.168.0-1.20-30\n'''
    if sys.version.startswith('3'):
        message += '[*] Example: ./ip_generator.py 192.168.0.0/24\n'
    return message


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(usage())
        exit()

    my_range = sys.argv[1]

    if '-' in my_range:
        if '/' in my_range:
            if sys.version.startswith('3'):
                print(usage())
                print("[-] Please either use CIDR notation or specify octet range with a dash ('-'), not both.")
                exit()
            if sys.version.startswith('2'):
                print(usage())
                print("[-] CIDR notation not supported with Python2. For CIDR notation, please use Python3.")
                exit()
        addresses = ip_range(my_range)

    elif '/' in my_range:
        if sys.version.startswith('2'):
            print(usage())
            print("[-] CIDR notation not supported when runnng this script with Python2. For CIDR notation, please use Python3.")
            exit()
        try:
            addresses = cidr_ip_range(my_range)
        except ValueError:
            print(usage())
            print('[-] Please do not specify host bits. Example: ./ip_generator.py 192.168.0.0/24')
            exit()
    
    for address in addresses:
        print(address)