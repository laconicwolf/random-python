# Python3
"""Performs multiple functions on strings to attempt
to match a known good token derived from a string or
multiple strings
"""
import argparse
import hashlib
import base64
import time

def sha1(string):
	"""Returns a sha1 hash of the supplied parameter
	"""
	return hashlib.sha1(string.encode()).hexdigest()


def md5(string):
	"""Returns a md5 hash of the supplied parameter
	"""
	return hashlib.md5(string.encode()).hexdigest()


def ripemd160(string):
    """Returns a ripemd160 hash of the supplied parameter
    """
    h = hashlib.new('ripemd160')
    h.update(string.encode())
    return h.hexdigest()


def build_strings(list_of_strings):
    """Accepts a list to be combined with various
    delimiters and returns a list of those strings
    """
    if len(list_of_strings) <= 1:
        return list_of_strings
    strings_list = []
    delims = [',', ':', ';', '&', '$']
    for delim in delims:
        strings_list.append(delim.join(list_of_strings))
        
    return strings_list


def rotate(l, n):
    """Rotates a list by n positions
    """
    return l[n:] +l[:n]


def main():
    """Rotates through a list of strings and performs operations to
    determine how a known good token me be derived
    """ 
    string_list = args.items
    if args.known_good_token:
        known_token = args.known_good_token
    for i in range(len(string_list)):
        j = 1 # index to loop through list and build each string
        for item in string_list:
            wordlist = string_list[:j]
            built_strings = build_strings(wordlist)
            for string in built_strings:
                if len(known_token) == 0 or len(known_token) == 40 or len(known_token) == 56:
                    sha1_hash = sha1(string)
                    if args.base64:
                        b64_sha1 = str(base64.b64encode(sha1_hash.encode()),'utf-8')
                    if args.verbose:
                        print("SHA1       : {}".format(sha1_hash))
                        if args.base64:
                            print("B64(SHA1)  : {}".format(b64_sha1))
                    if sha1_hash == known_token:
                        print('\n [+]  The token is derived from SHA1("{}"")'.format(string))
                        exit()
                    if b64_sha1 == known_token:
                        print('\n [+]  The token is derived from B64(SHA1("{}"")'.format(string))
                        exit()
                else:
                    if args.verbose:
                        print(" [*]  Skipping SHA1 because known good token length does not match SHA1")
                if len(known_token) == 0 or len(known_token) == 32 or len(known_token) == 44:
                    md5_hash = md5(string)
                    if args.base64:
                        b64_md5 = str(base64.b64encode(md5_hash.encode()),'utf-8')
                    if args.verbose:
                        print("MD5        : {}".format(md5_hash))
                        if args.base64:
                            print("B64(MD5)   : {}".format(b64_md5))
                    if md5_hash == known_token:
                        print('\n [+]  The token is derived from MD5("{}"")'.format(string))
                        exit()
                    if b64_md5 == known_token:
                        print('\n [+]  The token is derived from B64(MD5("{}""))'.format(string))
                        exit()
                else:
                    if args.verbose:
                        print(" [*]  Skipping MD5 because known good token length does not match MD5")
                if len(known_token) == 0 or len(known_token) == 40 or len(known_token) == 56:
                    ripemd160_hash = ripemd160(string)
                    if args.base64:
                        b64_ripemd160 = str(base64.b64encode(ripemd160_hash.encode()),'utf-8')
                    if args.verbose:
                        print("RIPEMD160:   {}".format(ripemd160_hash))
                        if args.base64:
                            print("B64(RIPEMD160): {}".format(b64_ripemd160))
                    if ripemd160_hash == known_token:
                        print('\n [+]  The token is derived from RIPEMD160("{}"")'.format(string))
                        exit()
                    if b64_ripemd160 == known_token:
                        print('\n [+]  The token is derived from B64(RIPEMD160("{}""))'.format(string))
                        exit()
                else:
                    if args.verbose:
                        print(" [*]  Skipping RIPEMD160 because known good token length does not match RIPEMD160")  
            j += 1
        string_list = rotate(string_list, i+1)
	
    print('Unable to derive token value')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-k", "--known_good_token", help="specify a known good token to compare against")
    parser.add_argument("-i", "--items", help="specify items to perform functions against", nargs='*')
    parser.add_argument("-b", "--base64", help="base64 encode outputs", action="store_true")
    args = parser.parse_args()

    if not args.items:
        print("\n [-]  You must specify one or more strings to perform functions on!\n")
        parser.print_help()
        exit()
    if not args.known_good_token:
        print("\n [*]  No known good token specified. If you want to view the output ensure you are writing to a file or using the -v flag.\n")
        known_token = ""
        time.sleep(3)
    if type(args.items) == str:
        args.items = [args.items]

    main()