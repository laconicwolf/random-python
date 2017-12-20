import xml.etree.ElementTree as etree
import os
import csv

filename = 'scan.xml'
csv_name = 'scan.csv'


def parse_xml_file(filename):
    tree = etree.parse(filename)
    root = tree.getroot()
    hosts = root.findall('host')
    scan_data = []
    host_data = []
    for host in hosts:
        if not host.findall('status')[0].attrib['state'] == 'up':
            continue
        ip_address = host.findall('address')[0].attrib['addr']
        host_name_element = host.findall('hostnames')
        try:
            host_name = host_name_element[0].findall('hostname')[0].attrib['name']
        except IndexError:
            host_name = ''
        print(host_name)
        port_element = host.findall('ports')
        ports = port_element[0].findall('port')
        port_data = []
        for port in ports:
            if not port.findall('state')[0].attrib['state'] == 'open':
                continue
            proto = port.attrib['protocol']
            port_id = port.attrib['portid']
            service = port.findall('service')[0].attrib['name']
            port_data.extend((ip_address, host_name, proto, port_id, service))
        host_data.append(port_data)
        for data in host_data:
            #print(data)
            chunks = [data[i:i + 5] for i in range(0, len(data), 5)]
            scan_data.append(chunks)

    return scan_data


def parse_to_csv(data):
    """Accepts a list and adds them to (or creates) a CSV file.
    """
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['IP', 'Host', 'Proto', 'Port', 'Service', 'Notes']
        csv_writer.writerow(top_row)
        print(' [+]  The file {} does not exist. New file created!'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError:
            print(" [-]  Permission denied to open the file {}. Check if the file is open and try again.".format(csv_name))
            for item in data:
                print(item)
            exit()
        csv_writer = csv.writer(csv_file)
        print(' [+]  {} exists. Appending to file!'.format(csv_name))
    
    for item in data:
        csv_writer.writerow(item)
        
    csv_file.close()        

data = parse_xml_file(filename)
parse_to_csv(data)