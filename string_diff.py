#!/usr/bin/env python

# Description: Compares two strings and outputs the 
# differences character by character.

# Author: Jake Miller (@LaconicWolf)
# Adapted from: 
# https://stackoverflow.com/questions/12226846/count-letter-differences-of-two-strings

# Output
'''
python3 string_diff.py "jake the snake is cool" "jake's a snake"
j = j
a = a
k = k
e = e
    '
t   s
h
e   a
  =
s = s
n = n
a = a
k = k
e = e

i
s

c
o
o
l
'''

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

for i, j in both:
    if i == j:
        print('{} = {}'.format(i, j))
    else:
        if not i:
            i = ' '
        if not j:
            j = ' '
        print('{}   {}'.format(i, j))