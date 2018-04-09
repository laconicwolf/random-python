# Not finished...

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('\nMissing module: {}'.format(missing_module))
    print('Try running "pip install {}", or do an Internet search for installation instructions.'.format(missing_module.strip("'")))
    exit()
import re
import argparse
import os
import random
import string
import threading
from queue import Queue
import csv
from sys import version
from time import sleep


if not version.startswith('3'):
    print('\nThis script has only been tested with Python3. If using another version and encounter an error, try using Python3\n')
    sleep(3)


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180408'
__version__ = '0.01'
__description__ = '''Multithreaded website scanner that fuzzes HTTP
                  headers.
                  '''


def get_random_useragent():
    ''' Returns a randomly chosen User-Agent string.
    '''
    win_edge = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    win_firefox = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/43.0'
    win_chrome = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
    lin_firefox = 'Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/42.0'
    mac_chrome = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.38 Safari/537.36'
    ie = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'

    ua_dict = {
        1: win_edge,
        2: win_firefox,
        3: win_chrome,
        4: lin_firefox,
        5: mac_chrome,
        6: ie
    }
    rand_num = random.randrange(1, (len(ua_dict) + 1))
    return ua_dict[rand_num]


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def get_host_headers():
    ''' Returns host headers values.
    '''
    random_string = get_random_string(10)
    headers = [random_string, '127.0.0.1', 'localhost', '"><img src=0 />']
    return headers


def get_useragent():
    random_string = get_random_string(30)
    user_agents = [random_string]


def make_request(url, header=None):
    ''' Builds a requests object, makes a request, and returns 
    a response object.
    '''
    s = requests.Session()
    
    if args.user_agent_header:
        if header = "User-Agent":
            user_agent = user_agent    
    else:
        user_agent = get_random_useragent()
    s.headers['User-Agent'] = user_agent

    if args.host_header:
        if host_header:
            s.headers['Host'] = host_header
    
    if args.proxy:
        s.proxies['http'] = args.proxy
        s.proxies['https'] = args.proxy
    
    resp = s.get(url, verify=False)
    return resp


def check_for_reflection(url, response, test_header, input_string):
    ''' Checks the contents of a response object for a specified input string
    and returns a message including attributes of the response and the response
    line where the reflection occurred.
    '''
    response_list = response.text.splitlines()
    relection = [line for line in response_list if input_string in line]
    msg = ''  
    if reflection:
        msg += "\n    URL: {}".format(url)
        msg += "\n    {}: {}".format(test_header, input_string)
        msg += "\n    Response code: {}".format(response.status_code)
        if len(reflection) > 1:
            for item in reflection:
                msg += "\n    Response: {}".format(item.strip())
        else:
            msg += "\n    Response: {}".format(reflection[0].strip())
    return msg, reflection


def parse_to_csv(data):
    ''' Takes a list of lists and outputs to a csv file.
    '''
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['URL', 'Host header', 'Status code', 'Header line text', 'Notes']
        csv_writer.writerow(top_row)
        print('\n[+] The file {} does not exist. New file created!\n'.format(csv_name))
    else:
        try:
            csv_file = open(csv_name, 'a', newline='')
        except PermissionError:
            print("\n[-] Permission denied to open the file {}. Check if the file is open and try again.\n".format(csv_name))
            exit()
        csv_writer = csv.writer(csv_file)
        print('\n[+]  {} exists. Appending to file!\n'.format(csv_name))
    
    for line in data:
        for item in line:
            csv_writer.writerow(item)
        
    csv_file.close()


def normalize_urls(urls):
    ''' Accepts a list of urls and formats them so they will be accepted.
    Returns a new list of the processed urls.
    '''
    url_list = []
    http_port_list = ['80', '280', '81', '591', '593', '2080', '2480', '3080', 
                  '4080', '4567', '5080', '5104', '5800', '6080',
                  '7001', '7080', '7777', '8000', '8008', '8042', '8080',
                  '8081', '8082', '8088', '8180', '8222', '8280', '8281',
                  '8530', '8887', '9000', '9080', '9090', '16080']                    
    https_port_list = ['832', '981', '1311', '7002', '7021', '7023', '7025',
                   '7777', '8333', '8531', '8888']
    for url in urls:
        if '*.' in url:
            url.replace('*.', '')
        if not url.startswith('http'):
            if ':' in url:
                port = url.split(':')[-1]
                if port in http_port_list:
                    url_list.append('http://' + url)
                elif port in https_port_list or port.endswith('43'):
                    url_list.append('https://' + url)
                else:
                    url = url.strip()
                    url = url.strip('/') + '/'
                    url_list.append('http://' + url)
                    url_list.append('https://' + url)
                    continue
            else:
                    url = url.strip()
                    url = url.strip('/') + '/'
                    url_list.append('http://' + url)
                    url_list.append('https://' + url)
                    continue
        url = url.strip()
        url = url.strip('/') + '/'
        url_list.append(url)
    return url_list


def scanner_controller(url):
    ''' Controls most of the logic for the script. Accepts a URL and calls 
    various functions to make requests and prints output to the terminal.
    Returns nothing, but adds data to the data variable, which can be used 
    to print to a file. 
    '''
    global data
    for header in headers_to_fuzz:
        url_data = []
        request_data = []
        if args.verbose:
            with print_lock:
                print("[*] Making HTTP request to {}".format(url))
        try:
            resp = make_request(url, header, value)
        except Exception as e:
            if args.verbose:
                print('[-] Unable to connect to site: {}'.format(url))
                print('[*] {}'.format(e))
            continue
        message, header_line = check_for_reflection(url, resp, header, resp.headers[header])
        if header_line:
            if len(header_line) > 1:
                header_line = '\n'.join(header_line)
            else:
                header_line = header_line[0]
        request_data.extend((url, header, resp.status_code, header_line))
        url_data.append(request_data)
    data.append(url_data)


def process_queue():
    ''' processes the url queue and calls the scanner controller function
    '''
    while True:
        current_url = url_queue.get()
        scanner_controller(current_url)
        url_queue.task_done()


def main():
    ''' Normalizes the URLs and starts multithreading
    '''
    processed_urls = normalize_urls(urls)
    
    for i in range(args.threads):
        t = threading.Thread(target=process_queue)
        t.daemon = True
        t.start()

    for current_url in processed_urls:
        url_queue.put(current_url)

    url_queue.join()

    if args.csv:
        parse_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-pr", "--proxy", help="Specify a proxy to use (-p 127.0.0.1:8080)")
    parser.add_argument("-csv", "--csv", nargs='?', const='results.csv', help="Specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-uf", "--url_file", help="Specify a file containing urls formatted http(s)://addr:port.")
    parser.add_argument("-hf", "--host_header_file", help="Specify a file containing host header values to use.")
    parser.add_argument("-hh", "--host_header", help="Fuzz the host header.", action="store_true")
    parser.add_argument("-uah", "--user_agent_header", help="Fuzz the user agent header.", action="store_true")
    parser.add_argument("-uahf", "--user_agent_header_file", help="Specify a file containing user agents to use.")
    parser.add_argument("-t", "--threads", nargs="?", type=int, default=1, help="Specify number of threads (default=1)")
    args = parser.parse_args()

    if not args.url_file:
        parser.print_help()
        print("\n [-]  Please specify an input file containing URLs. Use -uf <urlfile> to specify the file\n")
        exit()

    if args.url_file:
        urlfile = args.url_file
        if not os.path.exists(urlfile):
            print("\n [-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        urls = open(urlfile).read().splitlines()

    if not args.host_header and not args.user_agent_header:
        parser.print_help()
        print("\n [-]  Please specify a header or headers to test.\n")
        exit()

    headers_to_fuzz = []

    if args.host_header:
        headers_to_fuzz.append('host')

    if args.host_header_file:
        host_header_file = args.host_header_file
        if not os.path.exists(urlfile):
            print("\n [-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        host_headers = open(host_header_file).read().splitlines()
    else:
        host_headers = get_host_headers()

    if args.user_agent_header:
        headers_to_fuzz.append('User-Agent')

    if args.user_agent_header_file:
        user_agent_header_file = args.user_agent_header_file
        if not os.path.exists(urlfile):
            print("\n [-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        user_agent_headers = open(user_agent_header_file).read().splitlines()
    else:
        user_agent_headers = get_useragent()

    csv_name = args.csv

    # To disable HTTPS related warnings
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    print_lock = threading.Lock()

    url_queue = Queue()

    data = []

    main()