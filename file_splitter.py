import sys
import numpy

if len(sys.argv) != 3:
    print("\nUsage: file_splitter.py <input_file> <number of files to split the inputfile into>")
    print("Example: file_splitter.py big_file.txt 5")
    print("Makes a copy of big_file.txt and splits it into 5 new files.")
    exit()

filename = sys.argv[1]
num_files = int(sys.argv[2])

lines = open(filename).read().splitlines()
splits = numpy.array_split(lines, num_files)

counter = 1
for list in splits:
    fh = open(str(counter) + "_" + filename, 'w')
    for line in list:
        fh.write(line + '\n')
    fh.close()
    counter += 1