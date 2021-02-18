import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests

def get_js_urls(driver):
    return [i.get_attribute('src') for i in driver.find_elements(By.TAG_NAME,'script')]


def search_response(search_list, response):
    for item in search_list:
        index = response.text.find(item)
        if index > 0:
            print(f"{response.url} | {item}")


def main():
    driver.get(url)
    js_urls = []

    js_urls += get_js_urls(driver)

    for frame in driver.find_elements_by_tag_name('iframe'):
        driver.switch_to.frame(frame)
        js_urls += get_js_urls(driver)
        driver.switch_to.default_content()

    js_urls = list(filter(None, js_urls))

    print(f'All JS URLs from {url}')
    for i in js_urls: print(i)

    print('Fetching JS text...')
    responses = [requests.get(u) for u in js_urls]

    print('Searching the responses...')
    for response in responses:
        search_response(search_list, response)

    driver.quit()

    
if __name__ == "__main__":
    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--wordlist",
                        help="specify a file containing urls formatted http(s)://addr:port.")
    parser.add_argument("-uf", "--url_file",
                        help="specify a file containing urls formatted http(s)://addr:port.")
    parser.add_argument("-u", "--url",
                        help="specify a single url formatted http(s)://addr:port.")
    args = parser.parse_args()

    if not args.url and not args.url_file:
        print("[-] Please specify a URL (-u) or an input file containing URLs (-uf).")
        exit()
    if args.url and args.url_file:
        print("[-] Please specify a URL (-u) or an input file containing URLs (-uf). Not both")
        exit()
    if args.url_file:
        url_file = args.url_file
        if not os.path.exists(url_file):
            print("[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again")
            exit()
        with open(fname) as fh:
            urls = fh.read().splitlines()
    if args.url:
        urls = [args.url]

    for url in urls:
        if not url.startswith('http'):
            print("[-] Please specify a URL in the format proto://address:port (https://example.com:443).")
            exit()

    if args.wordlist:
        fname = args.wordlist
        if not os.path.exists(fname):
            print("[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again")
            exit()
        with open(fname) as fh:
            words = fh.read().splitlines()
        search_list = words
    else:
        search_list = '''
include
dependencies
require('''.splitlines()

    # Set some Chrome options
    options = Options()
    options.headless = True

    # You need the Chrome Webdriver in your path. 
    # Get it from: https://sites.google.com/a/chromium.org/chromedriver/downloads
    # Open a driver
    driver = webdriver.Chrome(options=options)

    main()
