#!/usr/bin/env python


__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180901'
__version__ = '0.01'
__description__ = """A program that aids in updating alt-text and alt-title for images."""


import argparse
import os

# Third-party modules
try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    from bs4 import BeautifulSoup as Bs
    from PIL import Image
except ImportError as error:
    missing_module = str(error).split(' ')[-1]
    print('[*] Missing module: {}'.format(missing_module))
    print('[*] Try running "pip install {}", or do an Internet search for installation instructions.'.format(missing_module.strip("'")))
    exit()



def get_wp_posts(endpoint_url):
    """Returns up to the last 100 posts as a list of dictionaries."""
    try:
        resp = requests.get(endpoint_url)
    except Exception as e:
        print("[-] An error occurred: {}".format(e))
    posts_data = resp.json()
    return posts_data


def parse_non_alt_text_images(post_data):
    """Parses HTML and returns a list of image URLs that do not have 
    alt-text or whose alt-text is ''.
    """
    image_urls = []
    html = Bs(post_data['content']['rendered'], "html.parser")
    images = html.find_all('img')
    for img in images:
        try: 
            alt_text = img['alt']
            if not alt_text:
                img_url = img.get('src')
                image_urls.append(img_url)
        except KeyError:
            img_url = img.get('src')
            image_urls.append(img_url)
    return image_urls


def make_dir(dir_name):
    """Creates a directory to store images if not already created."""
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)


def render_image(img_path):
    """Renders an image with the default viewer."""
    img = Image.open(img_path)
    img.show()


def download_image(img_url, directory):
    """Downloads an image to a specified directory."""
    local_filename = img_url.split('/')[-1]
    write_path = "{}{}{}{}{}".format(os.getcwd(), os.sep, directory, os.sep, local_filename)
    resp = requests.get(img_url, stream=True)
    with open(write_path, 'wb') as fh:
        for chunk in resp.iter_content(chunk_size=1024): 
            if chunk:
                fh.write(chunk)
    return write_path


def delete_file(filepath):
    """Deletes a file."""
    os.remove(filepath)


def delete_directory(dir_name):
    """Removes a directory."""
    os.rmdir(dir_name)


def main():
    posts_url = "{}/wp-json/wp/v2/posts?per_page=100".format(base_url)
    posts = get_wp_posts(posts_url)
    for post in posts:
        print("Title: {}".format(post.get('title')['rendered']))
        images = parse_non_alt_text_images(post)
        for img_url in images:
            print(img_url)
            if args.custom:
                temp_dir_name = 'img_temp'
                make_dir(temp_dir_name)
                image_path = download_image(img_url, temp_dir_name)
                render_image(image_path)
                delete_file(image_path)
                new_alt_text = input("Please enter the alt-text you would like to use for this image:\n")
            if args.auto:
                pass
        delete_directory(temp_dir_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", 
                        action="store_true",
                        help="Increase output verbosity")
    parser.add_argument("-a", "--auto", 
                        action="store_true",
                        help="Automatically populates image alt-text with tags/keywords")
    parser.add_argument("-c", "--custom", 
                        action="store_true",
                        help="Renders each image and prompts you to enter custom alt-text")
    parser.add_argument("-d", "--domain",
                        help="Specify the domain name of the WP site.")
    parser.add_argument("-u", "--username",
                        help="Specify a username for authentication.")
    parser.add_argument("-p", "--password",
                        help="Specify a password for authentication.")
    args = parser.parse_args()
    if not args.domain:
        parser.print_help()
        print("\n[-] Please specify the domain name of the wordpress site.\n")
        exit()
    if not args.auto and not args.custom:
        parser.print_help()
        print("\n[-] Please specify to perform either automatic alt-text (-a) or custom alt-text (-c).\n")
        exit()
    base_url = "http://{}".format(args.domain.strip('/'))

    main()