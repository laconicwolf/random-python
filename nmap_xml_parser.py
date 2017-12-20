import xml.etree.ElementTree as etree
import os
import csv
import argparse


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20171220'
__version__ = '0.01'
__description__ = '''Parses the xml output from an nmap scan. The user
                     can specify whether the data should be printed,
                     displayed as a list of IP addresses, or output to
                     a csv file. Will append to a csv if the filename
                     already exists'''


def get_xml_root(xml):
    """ Parses an xml file and returns the tree
    """
    tree = etree.parse(xml)
    root = tree.getroot()

    return root


def get_host_data(root):
    """ Goes through the xml tree and build lists of scan information
    and returns a list of lists.
    """
    host_data = []
    hosts = root.findall('host')
    for host in hosts:
        if not host.findall('status')[0].attrib['state'] == 'up':
            continue
        ip_address = host.findall('address')[0].attrib['addr']
        host_name_element = host.findall('hostnames')
        try:
            host_name = host_name_element[0].findall('hostname')[0].attrib['name']
        except IndexError:
            host_name = ''
        
        port_element = host.findall('ports')
        ports = port_element[0].findall('port')
        
        for port in ports:
            port_data = []
            if not port.findall('state')[0].attrib['state'] == 'open':
                continue
            proto = port.attrib['protocol']
            port_id = port.attrib['portid']
            service = port.findall('service')[0].attrib['name']

            try:
                script_id = ports[0].findall('script')[0].attrib['id']
                script_output = ports[0].findall('script')[0].attrib['output']
            except IndexError:
                script_id = ''
                script_output = ''
            port_data.extend((ip_address, host_name, proto, port_id, service, script_id, script_output))
            host_data.append(port_data)
    
    return host_data


def parse_xml():
    """ Calls functions to read the xml and extract elements and values
    """
    root = get_xml_root(filename)
    hosts = get_host_data(root)
    
    return hosts


def parse_to_csv(data):
    """Accepts a list and adds the items to (or creates) a CSV file.
    """
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['IP', 'Host', 'Proto', 'Port', 'Service', 'NSE Script ID', 'NSE Script Output', 'Notes']
        csv_writer.writerow(top_row)
        print(' [+]  The file {} does not exist. New file created!'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError:
            print("\n [-]  Permission denied to open the file {}. Check if the file is open and try again.\n".format(csv_name))
            print("Print data to the terminal:\n")
            for item in data:
                print(' '.join(item))
            exit()
        csv_writer = csv.writer(csv_file)
        print('\n [+]  {} exists. Appending to file!\n'.format(csv_name))
    
    for item in data:
        csv_writer.writerow(item)
        
    csv_file.close()        


def list_ip_addresses(data):
    """ Parses the input data to display only the IP address information
    """
    ip_list = []
    for item in data:
        ip_list.append(item[0])
    sorted_set = sorted(set(ip_list))
    for ip in sorted_set:
        print(ip)


def print_data(data):
    """ Prints the data to the terminal
    """
    for item in data:
        print(' '.join(item))


def main():
    data = parse_xml()
    if args.csv:
        parse_to_csv(data)
    if args.ip_addresses:
        list_ip_addresses(data)
    if args.print_all:
        print_data(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--print_all", help="display scan information to the screen", action="store_true")
    parser.add_argument("-ip", "--ip_addresses", help="display a list of ip addresses", action="store_true")
    parser.add_argument("-csv", "--csv", nargs='?', const='scan.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-f", "--filename", help="specify a file containing the output of an nmap scan in xml format.")
    args = parser.parse_args()

    if not args.filename:
        parser.print_help()
        print("\n [-]  Please specify an input file to parse. Use -f <nmap_scan.xml> to specify the file\n")
        exit()

    if not args.ip_addresses and not args.csv and not args.print_all:
        parser.print_help()
        print("\n [-]  Please choose an output option. Use -csv, -ip, or -p\n")
        exit()

    filename = args.filename
    csv_name = args.csv
    main()
