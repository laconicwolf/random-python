try:
    import argparse
    import requests
    import re
    import os
    import time
    import random
    import csv
    from requests.auth import HTTPBasicAuth
    from requests.auth import HTTPDigestAuth
    from requests_ntlm import HttpNtlmAuth
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


__author__ = 'Jake Miller'
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
        top_row = ['URL', 'Redirected URL', 'Title', 'Server', 'Notes']
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

    data = []
    print('\n [+]  Loaded {} URLs to check'.format(len(urls)))
    print(' [+]  Checking each URL...\n')

    for url in urls:
        site_data = []

        requestor = build_requests_object()     
        if args.verbose:
            print("\n [+]  Checking {}...".format(url))
        try:
            resp = requestor.get(url, verify=False, timeout=2)
        except:
            if args.verbose:
                print(' [-]  Unable to connect to site: {}'.format(url))
            continue

        title = check_site_title(resp, url)
        server = resp.headers['Server'] if 'Server' in resp.headers else ''
        redir_url = resp.url if resp.url.strip('/') != url else ""
        print(title)
        site_data.extend((url, redir_url, title, server))
        print(site_data)
        data.append(site_data)

    if args.csv:
        parse_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--proxy", help="specify a proxy to use (-p 127.0.0.1:8080)")
    parser.add_argument("-csv", "--csv", nargs='?', const='results.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-uf", "--url_file", help="specify a file containing urls formatted http(s)://addr:port.")
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
        
    csv_name = args.csv

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    main()