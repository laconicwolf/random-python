#!/usr/bin/env python3

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180710'
__version__ = '0.02'
__description__ = 'Accepts a domain name and queries multiple sources to return subdomains.'

import socket
import argparse
import re
import threading
from queue import Queue
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('[*] Missing module: {}'.format(missing_module))
    print('[*] Try running "pip install {}", or do an Internet search for installation instructions.'.format(
        missing_module.strip("'")))
    exit()


def search_censys(domain):
    """Returns subdomains scraped from censys.io."""
    url = "https://censys.io/certificates/_search?q=.{} and tags: unexpired&raw=true".format(domain)
    try:
        resp = requests.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []
    data = re.findall(r' parsed.names: (.*?)</mark>', resp.text)
    subs = [item.replace('<mark>', '') for item in data if domain in item]
    return list(set(subs))


def search_crt(domain):
    """Returns subdomains scraped from crt.sh."""
    url = "https://crt.sh/?q=%25.{}".format(domain)
    try:
        resp = requests.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []
    data = re.findall(r'<TD>(.*?)</TD>', resp.text)
    subs = [item for item in data if domain in item]
    return list(set(subs))


def search_dnsdumpster(domain):
    """Returns subdomains scraped from dnsdumpster.com."""
    url = "https://dnsdumpster.com/"
    s = requests.Session()
    try:
        resp = s.get(url)
        csrftoken = resp.cookies['csrftoken']
        s.headers['referer'] = url
        resp = s.post(url, {'csrfmiddlewaretoken': csrftoken, 'targetip': domain})
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []
    data = re.findall(r'<td class="col-md-4">(.*?)<br>\n<', resp.text)
    subs = [item for item in data if domain in item and ' ' not in item]
    return list(set(subs))


def search_virustotal(domain):
    """Returns subdomains scraped from virustotal.org."""
    url = "https://www.virustotal.com/en/domain/{}/information/".format(domain)
    try:
        resp = requests.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
        connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []
    data = re.findall(r'<a target="_blank" href="/en/domain/(.*?)/information/">\n', resp.text)
    subs = [item for item in data if domain in item]
    return list(set(subs))


def search_threatcrowd(domain):
    """Returns subdomains scraped from threatcrowd.org."""
    url = "https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={}".format(domain)
    try:
        resp = requests.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
        connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []
    data = resp.json().get('subdomains')
    if data is None:
        data = []
    subs = [item for item in data if domain in item]
    return list(set(subs))


def search_netcraft(domain):
    """Returns subdomains scraped from netcraft.com."""
    url = "https://searchdns.netcraft.com/?restriction=site+ends+with&host={}".format(domain)
    s = requests.Session()
    s.headers[
        'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    try:
        resp = s.get(url)
    except Exception as e:
        print('[-] Unable to connect to {}. Please check the network \
            connection, or manually verify the URL is still valid. Error: {}'.format(url, e))
        return []

    subs = []

    # Netcraft only shows 20 results at a time.
    # This is a result counter variable for querystring.
    i = 21

    # Continuously scrape until 'Next page' is not present.
    while True:
        if '"><b>Next page</b></a>' in resp.text:
            data = re.findall(r'\n<a href="(.*?)" rel="nofollow">', resp.text)
            subs += [item for item in data if domain in item]

            # The last result must be set in the querystring for
            # the next url to work. This regex grabs the last
            # result and strips it to the requirement.
            last_app = re.findall(r'\n<a href="(.*?)" rel="nofollow">', resp.text)[-1].split('//')[1].strip('/')

            next_url = 'https://searchdns.netcraft.com/?host={}&last={}&from={}&restriction=site ends with&position='.format(
                domain, last_app, str(i))
            resp = s.get(next_url)

            # Increment the counter to see the next 20 results
            i += 20
        else:
            data = re.findall(r'\n<a href="(.*?)" rel="nofollow">', resp.text)
            subs += [item for item in data if domain in item]
            break
    return list(set(subs))


def scan_host(host):
    """Attempts a TCP connection to a specified host. Updates
    the global scan_data variable with the hostname and ip address
    and return if the connection is successful."""
    global scan_data
    for port in [80, 443, 8080, 8443]:
        try:
            s = socket.socket()
            s.settimeout(args.timeout)
            s.connect((host, port))
            remote_ip = s.getpeername()[0]
            # remote_port = s.getpeername()[1]
            # remote_address = '{}:{}'.format(remote_ip, remote_port)
            scan_data.append((host, remote_ip))
            return
        except:
            continue


def process_queue(host_queue):
    """Processes the list of hosts to be scanned by scan_host"""
    while True:
        current_host = host_queue.get()
        scan_host(current_host)
        host_queue.task_done()


def main():
    """Main function of the script."""

    fh = open('subdomain_searcher_results.csv', 'a')
    subdomains = []
    if args.verbose:
        print("[*] Getting subdomains for {} from censys.io".format(domain))
    subdomains = search_censys(domain)
    if args.verbose:
        print("[*] Getting subdomains for {} from crt.sh".format(domain))
    subdomains += search_crt(domain)
    if args.verbose:
        print("[*] Getting subdomains for {} from dnsdumpster.com".format(domain))
    subdomains += search_dnsdumpster(domain)
    if args.verbose:
        print("[*] Getting subdomains for {} from virustotal.com".format(domain))
    subdomains += search_virustotal(domain)
    if args.verbose:
        print("[*] Getting subdomains for {} from threatcrowd.org".format(domain))
    subdomains += search_threatcrowd(domain)
    if args.verbose:
        print("[*] Getting subdomains for {} from netcraft.com".format(domain))
    subdomains += search_netcraft(domain)
    unique_subdomains = set(subdomains)
    if args.scan:
        if args.verbose:
            print(
                '[*] Performing scan on {} discovered subdomains to check connectivity'.format(len(unique_subdomains)))
        host_queue = Queue()
        for i in range(args.threads):
            t = threading.Thread(target=process_queue, args=[host_queue])
            t.daemon = True
            t.start()
        for unique_subdomain in unique_subdomains:
            host_queue.put(unique_subdomain)
        host_queue.join()

        print("[+] Subdomains found for {}:\n".format(domain))
        print('{:35}{:35}'.format("SUBDOMAIN", "IP ADDRESS"))
        for data in scan_data:
            sub_domain = data[0]
            sub_domain_address = data[1]
            fh.write('{},{}\n'.format(sub_domain, sub_domain_address))
            print('{:35}{:35}'.format(sub_domain, sub_domain_address))
    else:
        print("[+] Subdomains found for {}:\n".format(domain))
        for sub in unique_subdomains:
            if sub.startswith('http'):
                continue
            print(sub)
            fh.write('{}\n'.format(sub))
    fh.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity.",
                        action="store_true")
    parser.add_argument("-d", "--domain",
                        help="Specify the domain name to query subdomain for. \
Example: ./subdomain_searcher.py -d example.com")
    parser.add_argument("-s", "--scan",
                        help="Scan the discovered subdomains to check connectivity.",
                        action="store_true")
    parser.add_argument("-t", "--threads",
                        nargs="?",
                        type=int,
                        default=20,
                        help="Specify number of threads (default=20)")
    parser.add_argument("-to", "--timeout",
                        nargs="?",
                        type=int,
                        default=2,
                        help="Specify number of seconds until a connection timeout (default=2)")
    args = parser.parse_args()

    if not args.domain:
        parser.print_help()
        print('\n[-] You must specify a domain name!\n')
        exit()
    else:
        domain = args.domain

    # Suppress SSL warnings in the terminal
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    scan_data = []
    main()