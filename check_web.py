try:
    import argparse
    import requests
    import re
    import os
    import time
    from requests.auth import HTTPBasicAuth
    from requests.auth import HTTPDigestAuth
    from requests_ntlm import HttpNtlmAuth
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('\nThis script requires several modules that you may not have.')
    print('Missing module: {}'.format(missing_module))
    print('Try running "pip install {}", or do an Internet search for installation instructions.'.format(missing_module.strip("'")))
    exit()


__author__ = 'Jake Miller'
__date__ = '20171103'
__version__ = '0.01'
__description__ = '''A useful tool to gather information about services 
                listening on web ports.'''
                
                
def check_web(urls):
    ''' Takes a list of URLs and sends either a request object or silent browser
    to obtain title information. Returns two dictionaries: 1) Containing sites
    successfully browsed to that returned title, and sites successfully browsed to
    that required header authentication.
    '''
    web_ident = {}
    non_ident_auth = []
    if args.outfile:
        file = open(outfile,'a')
    print('\n [+]\tChecking each URL...\n')
    if type(urls) == str:
        urls = [urls]
    for url in urls:
        if not url.startswith('http'):
            url = http + url
        if args.verbose:
            print("\n [+]\tChecking {}...".format(url))
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=2)
        except:
            if args.verbose:
                print(' [-]\tUnable to connect to site: {}'.format(url))
        title = re.findall(r'<title[^>]*>([^<]+)</title>',resp.text, re.IGNORECASE)
        title = str(title).strip("[,],'")
        if title == "" and resp.status_code != 401:
            if args.verbose:
                print(' [-]\tThe title returned empty. Using browser emulation to get site title...')
                print('    \tThis could take ~10 seconds...')
            #TODO - CHANGE PHANTONJS USERAGENT
            browser = webdriver.PhantomJS()
            browser.get(url)
            WebDriverWait(browser, 2)
            title = browser.title
            browser.close()
        print(' [+]\tSite: {}'.format(url))
        print('    \tResponse Code: {}'.format(resp.status_code))
        if title == "":
            print('    \tTitle: Unable to parse title')
        else:
            try:
                print('    \tTitle: {}'.format(title))
            except UnicodeEncodeError:
                print('    \tTitle: {}'.format(title.encode('utf-8')))
        if args.outfile:
            try:
                file.write('Site: {}\tResponse Code: {}\tTitle: {}\n'.format(domain, resp.status_code, title))
            except UnicodeEncodeError:
                file.write('Site: {}\tResponse Code: {}\tTitle: {}\n'.format(domain, resp.status_code, title.encode('utf-8')))
            
        if resp.status_code == 401 and title == "":
            non_ident_auth.append(url)
        if str(resp.status_code).startswith('2') or str(resp.status_code).startswith('3') or resp.status_code == 401 and title != "":
            web_ident[url] = title        
    
    return web_ident, non_ident_auth
    

def check_creds_auth(sites):
    ''' Attempts to guess default credentials on sites requiring header authentication.
    Uses the file default_creds.py for username and password information.
    '''
    print('\n [+]\tChecking sites for header authentication...')
    creds = basic_auth_creds()
    for cred in creds:
        for k, v in cred.items():
            username = k
            password = v
        for url in sites:
            s = requests.Session()
            resp = s.get(url)
            if 'WWW-Authenticate' in resp.headers:
                auth_type = resp.headers['WWW-Authenticate']
                print('\n [+]\tTrying default credentials at {} using the following credentials:.'.format(url))
                print("    \t{} : {}".format(username, password))
                if auth_type == 'NTLM':
                    if not '@' in username:
                        domain = url.split('.')[-2:]
                        domain = ".".join(domain)
                        domain = domain.split(':')[0]
                        s.auth = HttpNtlmAuth(domain + '\\' + username, password)
                    else:
                        s.auth = HttpNtlmAuth(username, password)
                    resp = s.get(url, verify=False)
                    print(" [+]\tThe application responded with a code of {}.".format(str(resp.status_code)))
                    print(" [+]\tThe current URL is {}.".format(resp.url))
                    if resp.url.strip('/') != url:
                        print(' [+]\tPossible successful login due to redirect after login.')
                if auth_type == 'Basic':
                    pass
                if auth_type == 'Digest':
                    pass                
                
                
def check_creds(sites):
    ''' Attempts to guess default credentials on sites requiring form authentication.
    Uses the file default_creds.py for username, password and parameter information.
    '''
    creds = form_auth_creds()
    for item in sites:
        if sites[item].lower() in creds:
            s = requests.Session()
            site_title = sites[item].lower()
            data = creds[site_title]
            url = "{}{}".format(item, data[0])
            print(url)
            for i in range(1, len(data)):
                post_data = data[i]
                print('\n [+]\tTrying default credentials on {} at {} using the following POST data:.'.format(site_title.title(), url))
                print("    \t{}".format(post_data))
                resp = s.post(url, post_data, headers=headers, proxies=proxies, verify=False)
            
                print(" [+]\tThe application responded with a code of {}.".format(str(resp.status_code)))
                print(" [+]\tThe current URL is {}.".format(resp.url))
                if resp.url != url:
                    print(' [+]\tPossible successful login due to redirect after login.')
                #TODO - write to file or return the data
 

def main():
    form_auth_sites, auth_sites = check_web(urls)
    if args.checkcreds:
        if form_auth_sites != {}:
            check_creds(sites)
        if auth_sites != []:
            check_creds_auth(auth_sites)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-u", "--url", help="specify the url to check. Example: ./check_web.py -u https://site.example.com:8443")
    parser.add_argument("-i", "--infile", help="specify a file with a list of urls to check.")
    parser.add_argument("-o", "--outfile", help="specify the name of a file to write the results.")
    parser.add_argument("-cc", "--checkcreds", help="attempts to login with default credentials if website is known.", action="store_true")
    args = parser.parse_args()
    
    if not args.url and not args.infile:
        print('\n [-]\tYou must use either the -u option to specify a single url or the -i option to specify a file with multiple urls\n')
        parser.print_help()
        exit()
    
    if args.url and args.infile:
        print('\n [-]\tPlease use either the -u or the -i. Not both!\n')
        parser.print_help()
        exit()
        
    if args.url:
        urls = args.url
        
    if args.infile:
        if not os.path.isfile(args.infile):
            print('\n [-]\tUnable to find the file {}. Check the path and try again\n'.format(args.infile))
            parser.print_help()
            exit()
        try:    
            infile = open(args.checkcreds).read().splitlines()
        except PermissionError:
            print("\n [-]\tUnable to open the file {}. Check to see if the file is open, close the file, and try again.".format(args.infile))
            exit()
    
    if args.outfile:
        outfile = args.outfile
        
    if args.checkcreds:
        try:
            from default_credentials import form_auth_creds, header_auth_creds
            check_creds_file = 'checkcreds_out.txt'
            cc_file = open(check_creds_file,'a')
        except ImportError:
            print("\n [-]\tThe -cc (--checkcreds) option requires a file containing default credentials. See example at https://github.com/laconicwolf/subdomain_searcher\n")
            parser.print_help()
            exit()
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'https://127.0.0.1:8080',
    }
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    main()
