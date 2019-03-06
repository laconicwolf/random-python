#!/usr/bin/env python

import sys

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("Usage: python {} wordlist_to_mangle [outfile_name]".format(sys.argv[0]))
    exit()

infile = sys.argv[1]

if len(sys.argv) == 3:
    outfile = sys.argv[2]
else:
    outfile = None

word_dict = {
    'add': ['edit', 'delete', 'replace'],
    'edit': ['add', 'delete', 'replace'],
    'delete': ['edit', 'add', 'replace'],
    'replace': ['edit', 'add', 'delete'],
    'user': ['role'],
    'role': ['user'],
}

trigger_words = [
    'add',
    'edit',
    'delete',
    'replace',
    'user',
    'role'
]

with open(infile) as fh:
    wordlist = fh.read().splitlines()

new_wordlist = []

for trigger_word in trigger_words:
    for word in wordlist:
        if trigger_word in word:
            replacement_words = word_dict.get(trigger_word)
            for replacement_word in replacement_words:
                new_wordlist.append(word.replace(trigger_word, replacement_word))

for new_word in new_wordlist:
    print(new_word)