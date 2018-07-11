#!/usr/bin/env python3

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180711'
__version__ = '0.01'
__description__ = """Attempts a zone transfer for a specified domain."""

import os
import sys
import csv
import argparse
import whois
import dns.query
import dns.zone


def parse_to_csv(data, csv_name='zone_file.csv'):
    """Accepts a list of lists and adds the items to (or creates) a CSV file."""
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['Name', 'TTL', 'Record Class', 'Record Type', 'Record Data']
        csv_writer.writerow(top_row)
        print('[+] The file {} does not exist. New file created!\n'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError as e:
            print("[-] Permission denied to open the file {}. Check if the file is open and try again.\n".format(
                csv_name))
            print("[*] Printing data to the terminal:\n")
            for item in data:
                print(' '.join(item))
            exit()
        csv_writer = csv.writer(csv_file)
        print('\n[+] {} exists. Appending to file!\n'.format(csv_name))
    for item in data:
        for entry in item:
            csv_writer.writerow(entry)
    csv_file.close()


def parse_zone_row(zone_row, domain_name):
    """Parse an individual zone file row into the five zone file columns."""
    parsed_zone_row = []
    items = (zone_row.split(' '))
    if items[0].startswith('@'):
        items[0] = domain_name
    else:
        items[0] += '.{}'.format(domain_name)
    z_name = items[0]
    z_ttl = items[1]
    z_record_class = items[2]
    z_record_type = items[3]
    z_record_data = ' '.join(items[4:])
    parsed_zone_row.append([z_name, z_ttl, z_record_class, z_record_type, z_record_data])
    return parsed_zone_row


def parse_zone_list(zone_file_list, domain_name):
    """Takes a zone file as a list and returns it as a list of lists for easier csv parsing."""
    parsed_zone = []
    for line in zone_file_list:
        if line.startswith('@'):
            split_lines = line.split('\n')
            for l in split_lines:
                parsed_zone.append(parse_zone_row(l, domain_name))
        else:
            parsed_zone.append(parse_zone_row(line, domain_name))
    return parsed_zone


def get_nameservers(whois_data):
    """Parses the nameservers from a python-whois object"""
    return whois_data.get('name_servers')


def whois_lookup(domain_name):
    """Performs a whois lookup on the specified domain and returns the results"""
    try:
        result = whois.whois(domain_name)
    except Exception as error:
        print('[-] An error occurred: {}'.format(error))
        exit()
    return result


def transfer_zone(domain_name, nameserver):
    """Attempts a zone transfer for a specified domain name against a specified name server."""
    try:
        zone_data = dns.zone.from_xfr(dns.query.xfr(nameserver, domain_name))
    except dns.exception.FormError as error:
        print('Unable to transfer the zone file from {}'.format('domain_name'))
        return
    zone_list = []
    for entry in zone_data:
        zone_list.append((zone_data[entry].to_text(entry)))
    return zone_list


def main():
    global nameservers
    if not nameservers:
        whois_data = whois_lookup(domain_name)
        nameservers = get_nameservers(whois_data)
    if nameservers is None:
        print('[-] Unable to locate nameservers from the {} whois record. Try specifying a nameserver with the -n \
option (--nameserver). Exiting.'.format(domain_name))
        exit()
    for server in nameservers:
        zone_file = transfer_zone(domain_name, server)
        if zone_file:
            parsed_zone = parse_zone_list(zone_file, domain_name)
            print('[+] Zone transfer successful for {} against {}. Printing to zone_file.csv in the current directory'.format(domain_name, nameservers))
            parse_to_csv(parsed_zone)
        else:
            print('[-] Unable to perform a zone transfer for the domain {} using the nameserver {}'.format(domain_name, server))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--domain',
                        help='Specify a domain to attempt a zone transfer.')
    parser.add_argument('-n', '--nameserver',
                        help='Specify a nameserver to attempt a zone transfer.')
    args = parser.parse_args()
    if not args.domain:
        parser.print_help()
        print('\n[-] Please specify a domain name. Example: python3 {} -d example.com'.format(sys.argv[0]))
        exit()
    domain_name = args.domain
    if '.' not in domain_name:
        print('\n[-] Invalid domain name detected.')
        exit()
    if args.nameserver:
        nameservers = [args.nameserver]
    else:
        nameservers = []
    main()