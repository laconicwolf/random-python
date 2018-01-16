import ipaddress
import argparse
import os


__author__ = 'Jake Miller'
__date__ = '20180116'
__version__ = '0.01'
__description__ = ''' Creates a list of URLs to based on an supplied address range,
                      or an input file. Takes the addresses and prepends/appends the
                      appropriate proto/port. '''


http_port_list = ['80', '280', '81', '591', '593', '2080', '2480', '3080', 
                  '4080', '4567', '5080', '5104', '5800', '6080',
                  '7001', '7080', '7777', '8000', '8008', '8042', '8080',
                  '8081', '8082', '8088', '8180', '8222', '8280', '8281',
                  '8530', '8887', '9000', '9080', '9090', '16080']                    
https_port_list = ['832', '981', '1311', '7002', '7021', '7023', '7025',
                   '7777', '8333', '8531', '8888']


def main():
    for addr in addrs:
        for port in http_port_list:
            print("http://{}:{}".format(addr, port))
        for port in https_port_list:
            print("https://{}:{}".format(addr, port))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--range", help="specify the network range (10.10.10.0/24)")
    parser.add_argument("-i", "--input_filename", help="specify a file containing the a list of hosts to generate web addresses from.")
    args = parser.parse_args()

    if not args.input_filename and not args.range:
        parser.print_help()
        print("\n [-]  Please specify an input file (-i) to parse or an IP range (-r)\n")
        exit()

    if args.input_filename:
        if not os.path.exists(args.input_filename):
            parser.print_help()
            print("\n [-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        addrs = open(args.input_filename).read().splitlines()

    if args.range:
        addrs = []
        try:
            addr_obj = ipaddress.ip_network(args.range)
        except ValueError:
            parser.print_help()
            print('\n [-]  Please do not specify host bits. Example: -r 10.1.1.0/24\n')
            exit()
        for addr in addr_obj.hosts():
            addrs.append(addr)

    main()