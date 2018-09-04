from zipfile import ZipFile
import os
import platform
import shutil
import argparse


def create_directory(dirname):
    os.mkdir(dirname)


def read_file(filename):
    with open(filename, 'rb') as fh:
        contents = fh.read()

        return contents


def write_file(filename, contents):
    with open(filename, 'wb') as fh:
        fh.write(contents)


def list_files(filepath):
    file_listing = os.listdir(filepath)

    return file_listing


def extract_archive(filename, dest_dir):
    with ZipFile(filename) as myzip:
        myzip.extractall(dest_dir)


def remove_ole(contents):
                    #f   t   y   p 
    start_bytes = b'\x66\x74\x79\x70'
    index = contents.find(start_bytes)
    new_contents = b'\x00\x00\x00\x20' + contents[index:]
    return new_contents


def delete_directory(path):
    shutil.rmtree(path)


def main():
    create_directory(destination_dir)
    extract_archive(target_file, destination_dir)
    embedded_dir = destination_dir.strip(sep) + sep + "word" + sep + "embeddings" + sep
    object_listing = list_files(embedded_dir)
    for object in object_listing:
        obj_path = embedded_dir.strip(sep) + sep + object
        print(obj_path)
        contents = read_file(obj_path)
        new_contents = remove_ole(contents)

        target_filename = target_file.split(sep)[-1]
        new_filename = target_filename.split('.')[0] + '_' + object.replace('.bin', '.mp4')
        print(new_filename)
        write_file(new_filename, new_contents)
    delete_directory(destination_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="specify a file containing the embedded object")
    args = parser.parse_args()

    if not args.filename:
        parser.print_help()
        print("\n[-] Please specify an input file containing the embedded object\n")
        exit()

    if not os.path.exists(args.filename):
        print("\n[-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
        exit()
        
    target_file = args.filename
    destination_dir = target_file + 'extracted'

    sep = '\\' if platform.system() == 'Windows' else '/'

    main()
