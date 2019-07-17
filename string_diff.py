#!/usr/bin/env python

# Description: Compares two strings and outputs the 
# differences character by character.

# Author: Jake Miller (@LaconicWolf)
# Adapted from: 
# https://stackoverflow.com/questions/12226846/count-letter-differences-of-two-strings

import sys

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

usage = "Usage: ./string_diff.py <string1> <string2>"

if len(sys.argv) != 3:
    print(usage)
    exit()

string1 = sys.argv[1]
string2 = sys.argv[2]

try:
    both = zip_longest(string1, string2)
except Exception as e:
    print('[-] An error occurred: \n'.format(e))
    exit()

print('Pos   S1  S2\n')

char_num = 0
for i, j in both:
    char_num += 1
    char_pos = str(char_num)
    while len(char_pos) < 6:
        char_pos += ' '
    if i == j:
        print('{}{} = {}'.format(char_pos, i, j))
    else:
        if not i:
            i = ' '
        if not j:
            j = ' '
        print('{}{}   {}'.format(char_pos, i, j))
