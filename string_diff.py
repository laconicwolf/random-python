#!/usr/bin/env python

import sys

usage = "Usage: ./string_diff.py <string1> <string2>"

if len(sys.argv) != 3:
    print(usage)
    exit()

string1 = sys.argv[1]
string2 = sys.argv[2]

both = zip(string1, string2)
for i, j in both:
    if i == j:
        print i, '--', j
    else: 
        print i, '  ', j