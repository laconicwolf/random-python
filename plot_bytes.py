#!/usr/bin/env python3

__author__ = 'Jake Miller (@LaconicWolf)'
__date__ = '20180514'
__version__ = '0.01'
__description__ = """A program to plot byte values for a given set of data"""


import matplotlib.pyplot as plt 
import base64
import urllib.parse
import argparse
import os
import sys


def decode_url_encoding(input_string):
    """Returns a URL decoded byte-string
    """
    if type(input_string) == bytes:
        input_string = input_string.decode()
    if '%' not in input_string:
        return input_string.encode()
    return urllib.parse.unquote(input_string).encode()


def get_integer_list(input_bytes):
    return [byte for byte in input_bytes]


def main():
    data = input_data
    if type(data) == str:
        data = data.encode()
    if args.url_decode:
        data = decode_url_encoding(data)
    if args.b64_decode:
        data = base64.b64decode(data)
    data_list = get_integer_list(data)
    integer_list = [i for i in range(256)]
    if args.plot_histogram:
        plt.hist(data_list, color='g')
        plt.title('Byte Histogram')
        plt.ylabel('Occurence')
        plt.xlabel('Byte Values')
        plt.xticks(range(0, 256, 10))
        plt.show()
    if args.plot_scatter:
        positions = [i for i in range(len(data_list))]
        plt.scatter(data_list, positions, edgecolors='r')
        plt.title('Byte Scatter Plot')
        plt.ylabel('Occurence')
        plt.xlabel('Byte Values')
        plt.xticks(range(0, 256, 10))
        plt.show()
    print(data[:50])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity", 
                        action="store_true")
    parser.add_argument("-ph", "--plot_histogram",
                        help="Plot at histogram.", 
                        action="store_true")
    parser.add_argument("-ps", "--plot_scatter",
                        help="Plot as scatter.", 
                        action="store_true")
    parser.add_argument("-d", "--data",
                        help="Specify the data as a string.")
    parser.add_argument("-f", "--file",
                        help="Specify a file containing the data.")
    parser.add_argument("-u", "--url_decode",
                        help="Decode the URL encoded characters", 
                        action="store_true")
    parser.add_argument("-b", "--b64_decode",
                        help="Decode the b64 encoded data", 
                        action="store_true")
    args = parser.parse_args()

    if not args.data and not args.file:
        parser.print_help()
        print('\n[-] Please specify the encrypted data (-d data) or specify a file containing the data (-f /path/to/data) ')
        exit()
    if args.data and args.file:
        parser.print_help()
        print('\n[-] Please specify either -d or -f, not both.')
        exit()
    if args.data:
        input_data = args.data
    if args.file:
        if not os.path.exists(args.file):
            print("\n[-] The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        else:
            input_data = open(args.file, 'rb').read()
    main()
