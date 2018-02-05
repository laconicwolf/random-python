try:
    import argparse
    import requests
    import re
    import os
    import time
    import random
    import csv
    import threading
    from queue import Queue

    # need these if I implement authentication testing
    #from requests.auth import HTTPBasicAuth
    #from requests.auth import HTTPDigestAuth
    #from requests_ntlm import HttpNtlmAuth
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from selenium import webdriver
    from selenium.webdriver import DesiredCapabilities
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('\nThis script requires several modules that you may not have.')
    print('Missing module: {}'.format(missing_module))
    print('Try running "pip install {}", or do an Internet search for installation instructions.'.format(missing_module.strip("'")))
    exit()


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180104'
__version__ = '0.02'
__description__ = ''' A useful tool to gather information about services 
                listening on web ports. '''


def build_requests_object():
    ''' Returns a Session() instantiated requests object with a 
    random user agent
    '''
    s = requests.Session()
    user_agent = get_random_useragent()
    s.headers['User-Agent'] = user_agent
    if args.proxy:
        s.proxies['http'] = args.proxy
        s.proxies['https'] = args.proxy

    return s


def check_site_title(resp_obj, url):
    ''' Parses the title from a response object. If the title returns empty,
    a silent selenium browser is used to gather the title.
    '''
    if 'WWW-Authenticate' in resp_obj.headers:
        auth_type = resp_obj.headers['WWW-Authenticate']
        title = "Requires {} authentication".format(auth_type)

        return title

    title = re.findall(r'<title.*?>(.+?)</title>',resp_obj.text, re.IGNORECASE)
    if title == []:
        if args.verbose:
            print(" [+]  Browsing to the url with PhantomJS")
        try:
            desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
            desired_capabilities['phantomjs.page.customHeaders.User-Agent'] = get_random_useragent()
            browser = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
        except:
            # If PhantomJS is not installed, a blank title will be returned
            if args.verbose:
                print(" [-] An error occurred with PhantomJS")
            title == ""
            
            return title

        browser.get(url)
        WebDriverWait(browser, 2)
        title = browser.title
        if args.screenshot_no_title and title == '':
            screen_shot_name = url.split('//')[1].split(':')[0]
            browser.save_screenshot(screen_shot_name + '.png')
        browser.close()

    else: 
        title = title[0]

    return title


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


def parse_to_csv(data):
    ''' Takes a list and outputs to a csv file.
    '''
    if not os.path.isfile(csv_name):
        csv_file = open(csv_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        top_row = ['URL', 'Redirected URL', 'Title', 'Server', 'Dirs', 'Notes']
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


def directories():
    ''' Returns a list of directories to be browsed.
    '''
    dirs = ['/oam/auth/auth_cred_submit', '/iam', '/server-status']

    return dirs


def print_data(data):
    ''' Prints the data to the terminal
    '''
    # removes newlines from the directory item if exists
    if '\n' in data[4]:
        data[4] = data[4].replace('\n', ' ')
    print(' '.join(data))


def bust_dirs(url, dirbust_dir, server, title, req_obj):
    ''' Browses to a specified directory and checks the response to see
    if the directory returns a response that indicates a resource exists
    at that directory
    '''
    url_dir = url + dirbust_dir
    try:
        resp = req_obj.get(url_dir, verify=False, timeout=2)
    except:
        if args.verbose:
            print(' [-]  Unable to connect to site: {}'.format(url))
        return ""

    # resp.ok will be True on a redirect, so this makes sure the request wasn't redirected
    if resp.ok and resp.url.strip('/') == url_dir and not 'burp suite professional' in title.lower():
        return dirbust_dir
    else:
        return ""


def main(url):
    ''' Main function where the action happens
    '''
    # fetches url from the queue
    url = url.get()

    # intialize empty list to store data 
    site_data = []

    # builds a request object with a random user agent and proxy if specified
    requestor = build_requests_object()

    # attempts to connect to the site
    if args.verbose:
        print("\n [+]  Checking {}...".format(url))
    try:
        resp = requestor.get(url, verify=False, timeout=2)
    except:
        if args.verbose:
            print(' [-]  Unable to connect to site: {}'.format(url))
        url_queue.task_done()
        return

    # checks the site's title, server, and redirect url. Returns "" if it doesn't exist
    title = check_site_title(resp, url)
    server = resp.headers['Server'] if 'Server' in resp.headers else ""
    redir_url = resp.url if resp.url.strip('/') != url else ""

    # initializes empty list to contain valid directories, and dirbusts if option is specified
    dirs = []
    if args.dirbust:
        for dirbust_dir in dirbust_dirs:
            found_dir = bust_dirs(url, dirbust_dir, server, title, requestor)
            dirs.append(found_dir)
    directories = '\n'.join(dirs)
    
    # populates the site_data variable with all of the captured data
    site_data.extend((url, redir_url, title, server, directories))

    # prints output to the screen
    if args.print_all or args.verbose:
        print_data(site_data)

    # populates site_data too the data list
    data.append(site_data)

    # reports task done to the queue
    url_queue.task_done()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--print_all", help="display scan information to the screen", action="store_true")
    parser.add_argument("-snt", "--screenshot_no_title", help="Takes a screenshot if no title is found", action="store_true")
    parser.add_argument("-d", "--dirbust", default='common', const='common', nargs='?', choices=['common', 'file'], help="Attempts to dirbust common or file-specified directories")
    parser.add_argument("-df", "--dirbust_file", help="Specify text file containing directories to test, one directory per line.")
    #parser.add_argument("-s", "--screenshot", help="Takes a screenshot of each page", action="store_true")
    parser.add_argument("-pr", "--proxy", help="specify a proxy to use (-pr 127.0.0.1:8080)")
    parser.add_argument("-csv", "--csv", nargs='?', const='results.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-uf", "--url_file", help="specify a file containing urls formatted http(s)://addr:port.")
    parser.add_argument("-t", "--threads", nargs="?", type=int, default=1, help="specify number of threads (default=1)")
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
        
    if not args.print_all and not args.verbose and not args.csv:
        parser.print_help()
        print("\n [-]  Please specify an output option. Use -p to print to screen and/or -csv to output to a CSV file.\n")
        exit()

    if args.dirbust_file and not args.dirbust:
        print("\n [-]  The '-d file' argument is required if you want to use the '-df <filename>' option\n")
        exit()  

    if args.dirbust == 'file' and not args.dirbust_file:
        print("\n [-]  The '-df <filename>' argument is required if you want to use the '-d file' option\n")
        exit() 

    if args.dirbust == 'common' and args.dirbust_file:
        print("\n [-]  The '-d common' argument does not require a file and will only include the directories defined in the directories() function. The '-df <filename>' argument is required if you want to use the '-d file' option\n")
        exit() 

    if args.dirbust:
        if args.dirbust_file and args.dirbust == 'file':
            try:
                os.path.isfile(args.dirbust_file)
            except:
                print('\n [-]  There was an error loading the file. Exiting.\n')
                exit()               
            dirbust_dirs = open(args.dirbust_file).read().splitlines()
        else:
            dirbust_dirs = directories()
        
    csv_name = args.csv

    # suppress SSL warnings in the terminal
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    # initiates the queue
    url_queue = Queue()

    print('\n [+]  Loaded {} URLs to check\n'.format(len(urls)))

    # initialize the main data list that will be appended to for each url requested
    data = []

    # initializes threads. This is definitely not the best way to do things...
    worker_threads = []
    thread_counter = 0
    thread_max = args.threads

    for url in urls:
        url_queue.put(url)
        thread_counter += 1
        if thread_counter == thread_max:
            
            # should be enough time for the threads to finish. Kinda hacky but oh well ;)
            time.sleep(5)
            thread_counter = 0
    
        for i in range(1):
            worker_thread = threading.Thread(target=main, args=(url_queue,))
            worker_threads.append(worker_thread)
            worker_thread.start()

    for worker_thread in worker_threads:
        worker_thread.join()

    if args.csv:
        parse_to_csv(data)
