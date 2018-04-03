import ipaddress
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


def range_maker(ip_range):
    """ Returns a list of ip addresses when provided
    a dash specified address range (10.1.1.0-30).
    """
    addrs = []
    index = ip_range.index('-')
    start = ip_range[:index]
    end = ip_range[index + 1:]

    if len(start.split('.')) == 4:
        oct_1 = start.split('.')[0]
        oct_2 = start.split('.')[1]
        oct_3 = start.split('.')[2]
        s_range = start.split('.')[3]

    if len(start.split('.')) == 3:
        oct_1 = start.split('.')[0]
        oct_2 = start.split('.')[1]
        s_range = start.split('.')[2]

    if len(start.split('.')) == 2:
        oct_1 = start.split('.')[0]
        s_range = start.split('.')[1]

    if len(start.split('.')) == 1:
        s_range = start.split('.')[0]

    if len(end.split('.')) == 4:
        e_range = end.split('.')[0]
        oct_2 = end.split('.')[1]
        oct_3 = end.split('.')[2]
        oct_4 = end.split('.')[3]
        range_list = range(int(s_range), int(e_range) + 1)
        for i in range_list:
            addrs.append('{}.{}.{}.{}'.format(str(i), oct_2, oct_3, oct_4))
        return addrs

    if len(end.split('.')) == 3:
        e_range = end.split('.')[0]
        oct_3 = end.split('.')[1]
        oct_4 = end.split('.')[2]
        range_list = range(int(s_range), int(e_range) + 1)
        for i in range_list:
            addrs.append('{}.{}.{}.{}'.format(oct_1, str(i), oct_3, oct_4))
        return addrs

    if len(end.split('.')) == 2:
        e_range = end.split('.')[0]
        oct_4 = end.split('.')[1]
        range_list = range(int(s_range), int(e_range) + 1)
        for i in range_list:
            addrs.append('{}.{}.{}.{}'.format(oct_1, oct_2, str(i), oct_4))
        return addrs

    if len(end.split('.')) == 1:
        e_range = end.split('.')[0]
        range_list = range(int(s_range), int(e_range) + 1)
        for i in range_list:
            addrs.append('{}.{}.{}.{}'.format(oct_1, oct_2, oct_3, str(i)))
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
            if len(args.range.split('-')) > 2:
                print("\n[-] Unable to parse ranges in multiple octets. Please only use a '-' in one octet. Example -r 10.1.1.50-65\n")
                exit()
            addrs = range_maker(args.range)
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
