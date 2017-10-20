#download_extract.py

import urllib.request
import shutil
import argparse
import platform
import os
import time
from zipfile import ZipFile

def download_file(url):
    """Download the file from 'url' and save it locally 
    under 'file_name'
    """
    file_name = url.split('/')[-1]
    #TODO: Check for network or HTTP errors
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
        #TODO: Check if file already exists
        shutil.copyfileobj(response, out_file)
    return file_name
        

def make_directory(name):
    """Creates a unique directory from a given file name
    """
    file_name = name
    if '.' in file_name:
        file_name = file_name.split('.')[0]
    timestr = time.strftime("%Y%m%d-%H%M%S")
    unique_name = file_name + '-' + timestr
    os.makedirs(unique_name)
    return name, unique_name
    
    
def extract(file_name, location):
    """Extracts specified files to a specified directory
    """
    with ZipFile(file_name) as zf:
        zf.extractall(location,pwd=password)
    
if __name__ == '__main__':                                
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="Enter URL and file name. Example: python download_extract.py -u http://me.com/file.zip")
    parser.add_argument("-p", "--password", default='infected') 
    args = parser.parse_args()
	
    if not args.url:
        parser.print_help()
        exit()
    elif not args.url.startswith("http"):
        print('The url must start with http\n')
        parser.print_help()
        exit()
    url = args.url
    password = bytes(args.password, encoding='utf-8')
    if platform.system() == 'Windows':
        sep = '\\'
    else:
        sep = '/'
    download_name = download_file(url)
    archive_name, directory_name = make_directory(download_name)
    extract(archive_name, directory_name)
    