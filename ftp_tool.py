import ipaddress
import itertools
import argparse
import ftplib
import os
import csv


def ftp_anon_login(ftp_obj):
    """ Attempts to anonymously login to an FTP server
    """
    login_message = ''
    try:
        login_message = ftp_obj.login()
    except ftplib.all_errors:
        pass

    return login_message


def parse_to_csv(data):
    """Accepts a list and adds the items to (or creates) a CSV file.
    """
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['IP Addr', 'Port', 'Banner', 'Anonyomous Login', 'Directory Listing', 'Credentials', 'Notes']
        csv_writer.writerow(top_row)
        print('\n[+] The file {} does not exist. New file created!\n'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError:
            print("\n[-] Permission denied to open the file {}. Check if the file is open and try again.\n".format(csv_name))
            print("Printing data to the terminal:\n")
            for item in data:
                print(' '.join(item))
            exit()
        csv_writer = csv.writer(csv_file)
        print('\n[+] {} exists. Appending to file!\n'.format(csv_name))
    
    for item in data:
        csv_writer.writerow(item)
        
    csv_file.close()        


def list_directories(ftp_obj):
    """ Performs a directory listing on an FTP object
    """
    try:
        dirlist = ftp_obj.nlst()
    except ftplib.all_errors:
        return ""

    return '\n'.join(dirlist)


def ip_range(input_string):
    """ Accepts a '-' specified ip range and returns a list
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
                anonymous_login = "True"
            else:
                print('[-] {0}:{1} - Unable to log in. Permission Error'.format(addr, port))
                anonymous_login = "False"
        else:
            anonymous_login = ""

        if args.list_dir:
            dirs = ''
            if anonymous_login == "True":
                try:
                    dirs = list_directories(ftp)
                    if args.verbose:
                        print('[+] {0}:{1} - Directory Listing:'.format(addr, port))
                        print(dirs)
                except:
                    dirs = ''
        else:
            dirs = ''

        host_data.extend((addr, port, banner, anonymous_login, dirs))
        data.append(host_data)

    if args.csv:
        parse_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-r", "--range", help="specify the network range (10.10.10.0/24 or 10.10.10.20-40")
    parser.add_argument("-i", "--ipaddress", help="specify IP address of the FTP server")
    parser.add_argument("-p", "--port", type=int, nargs="?", default='21', help="specify a port. Default is 21")
    parser.add_argument("-f", "--input_filename", help="specify a file containing the a list of hosts to generate web addresses from.")
    parser.add_argument("-a", "--anon_login", help="attempt to anonymously login to the FTP server", action="store_true")
    parser.add_argument("-l", "--list_dir", help="lists directories (one deep) if login is allowed. Use recurse (-r) as well for full listing", action="store_true")
    #parser.add_argument("-rec", "--recurse", help="recursively list directories. Requires -l as well.", action="store_true")
    parser.add_argument("-csv", "--csv", nargs='?', const='ftp_results.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    args = parser.parse_args()

    if not args.input_filename and not args.range and not args.ipaddress:
        parser.print_help()
        print("\n[-] Please specify an input file (-f) to parse or an IP range (-r)\n")
        exit()

    if args.input_filename:
        if not os.path.exists(args.input_filename):
            parser.print_help()
            print("\n[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
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

    csv_name = args.csv
    port = args.port
    print("\n [+]  Loaded {} FTP server addresses to test\n".format(str(len(addrs))))

    main()
