import sys
import re
from pathlib import Path

__author__ = 'Jake Miller'
__date__ = '20171013'
__version__ = '0.01'
__description__ = 'Trims a password list to meet certain criteria'

if len(sys.argv) != 2:
    print('Usage: ./password_trimmer.py [filename]')
    print('Output will be written to trimmed_[filename]')
    exit()

infile = sys.argv[1]
outfile = 'trimmed_' + infile 

if not Path(infile).is_file():
    print('The file {} could not be found. Please try again'.format(infile))
    exit()

trimmed_list = []

with open(infile) as file:
    for line in file:
        if re.search(r'\W', line.strip()):
            continue
        if not len(line.strip()) == 8:  
            continue
        if not line[0].isalpha():
            continue
        if not re.search(r'[A-Z]', line.strip()):
            continue
        if not re.search(r'[a-z]', line.strip()):
            continue
        if not re.search(r'[0-9]', line.strip()):
            continue
        trimmed_list.append(line)

with open(outfile, 'w') as file:
    for word in trimmed_list:
        file.write(word)
        
print('Password list trimming complete! Trimmed to {} words.'.format(len(trimmed_list)))