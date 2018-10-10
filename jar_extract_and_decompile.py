#!/usr/bin/env python3

import os
import argparse
from pathlib import Path
from zipfile import ZipFile
import subprocess
import time


__author__ = 'Jake Miller'
__date__ = '20171026'
__version__ = '0.01'
__description__ = '''Extracts the contents of all .jar files in the current directory 
            to a new folder, then walks the new folder along with any subfolders 
            looking for .class files. Passes a list of all .class files to a separate
            java decompiler and writes the output of the decompiled java files to a text 
            file. Includes option to rewrite all .class files as .java files for use in
            an IDE.
            '''

            
def make_directory():
    """Creates a unique directory
    """
    dir_name = 'archive_extracts'
    timestr = time.strftime("%Y%m%d-%H%M%S")
    unique_name = dir_name + '-' + timestr
    os.makedirs(unique_name)
    
    return unique_name


def get_jar_files():
    """Returns all .jar files in the current directory
    except for the cfr decompiler program
    """
    jar_files = []
    items = os.listdir()
    for item in items:
        if item.endswith('.jar') or item.endswith('.war') or item.endswith('ear') and not item == java_decompiler:
            jar_files.append(item)
    
    return jar_files

    
def extract_jar(location, jars):
    """Extracts the contents of .jar files to a specified location
    """
    for jar in jars:
        with ZipFile(jar) as zf:
            zf.extractall(location)


def get_class_files():
    """Returns all .class files in current folder
    and subfolders.
    """
    class_files = []
    for root, dirs, files in os.walk(".", topdown = False):
        for name in files:
            if name.endswith('.class'):
                class_files.append(os.path.join(root, name))
        for name in dirs:
            if name.endswith('.class'):
                class_files.append(os.path.join(root, name))
    
    return class_files


def delete_class_files(dir):
    """Deletes all .class files in current folder
    and subfolders.
    """
    for root, dirs, files in os.walk(dir, topdown = False):
        for name in files:
            if name.endswith('.class'):
                os.remove(os.path.join(root, name))
        for name in dirs:
            if name.endswith('.class'):
                os.remove(os.path.join(root, name))
    
    
def decompile_class_files(class_files):
    """Uses the cfr Java decompiler in current directory to 
    decompile all class files and write the output to a file.
    If --makejava is used then all output will be rewritten as
    individual ,java files in addition to the textfile output.
    """
    outfile_name = 'decompiled_classes.txt'
    with open(outfile_name, 'a') as outfile:
        total_class_files = len(class_files)
        class_file_counter = 1
        for file in class_files:
            if args.verbose:
                print("[+] Processing file {} of {}".format(str(class_file_counter), str(total_class_files)))
            decompiled_output = subprocess.getoutput("java -jar " + java_decompiler + " " + file)
            if args.makejava:
                newfile = file.replace('.class', '.java')
                with open(newfile,'w') as new_file:
                    new_file.write(decompiled_output)
            outfile.write("-" * 90)
            outfile.write('\n{}\n'.format(file))
            outfile.write(decompiled_output + '\n')
            class_file_counter += 1
    
    return outfile_name

    
def main():
    print('[*] Looking for .jar files in the current directory')
    jar_files = get_jar_files()
    dir = make_directory()
    print('[+] Extracting files to the folder {}'.format(dir))
    extract_jar(dir, jar_files)
    print('[*] Looking for .class files in {} and its subfolders'.format(dir))
    class_files = get_class_files()
    print('[*] Decompiling {} class files. Please wait.'.format(str(len(class_files))))
    outfile = decompile_class_files(class_files)
    print('[+] Decompiling complete! Results written to the file {}.'.format(outfile))
    if args.makejava:
        print('[+] All .class files have been written to .java files in the {} folder.'.format(dir))
        delete_files = input("\n[?] Would you like to delete all .class files in the {} folder? Type Y or N:\n".format(dir))
        if delete_files.lower().startswith('y'):
            print("\n[*] Cleaning up...")
            delete_class_files(dir)
    

if __name__ == '__main__': 
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--decompiler", default='cfr_0_128.jar', help="specify the path to the decompiler")
    parser.add_argument("-m", "--makejava", help="decompiles all .class files and writes to a new .java file", action="store_true")
    args = parser.parse_args()
          
    java_decompiler = args.decompiler
    if not Path(java_decompiler).is_file():
        print('\n[-] The file {} could not be found in the current directory. Please try again'.format(java_decompiler))
        exit()
    main()