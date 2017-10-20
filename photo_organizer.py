import shutil, os, platform
import exifread

   
def convert_month_to_number(month):
    '''Receives a string month and returns the number equivalent
    For example, October as input will return 10
    '''
    if month.lower() == 'january':
        return "1"
    elif month.lower() == 'february':
        return "2"
    elif month.lower() == 'march':
        return "3"
    elif month.lower() == 'april':
        return "4"
    elif month.lower() == 'may':
        return "5"
    elif month.lower() == 'june':
        return "6"  
    elif month.lower() == 'july':
        return "7"
    elif month.lower() == 'august':
        return "8"
    elif month.lower() == 'september':
        return "9"
    elif month.lower() == 'october':
        return "10"
    elif month.lower() == 'november':
        return "11"   
    elif month.lower() == 'december':
        return "12"


def setup_photos():
    '''Examines folders in current directory and looks for folders
    containing a month. Will create a new empty folder for any folder
    that has a month and year name but not formatted year-month (2016-11)
    Returns a list of folders to extract photos from.
    '''
    for folder in folders:
        folder = folder.lower()
        photo_file_check = 0
        if os.path.isdir(folder):
            for month_name in month_list:
                if month_name in folder:
                    photo_file_check = 1
            if photo_file_check == 1:
                month = folder.strip(",").split()[0].lower()
                if month not in month_list:
                    parts = folder.split()
                    for part in parts:
                        if part.lower() in month_list:
                            month = part.lower()
                month = convert_month_to_number(month)
                try:
                    year = folder.split()[-1].lower()
                except IndexError:
                    continue
                if not year.startswith('2'):
                    print("Please make sure each folder ends with a year")
                    exit()
                photo_folders.append(folder)
                foldername_format = ("{}-{}".format(year, month))
                folder_names.append(foldername_format)
        
    new_folder_names = (set(folder_names))
    for new_folder in new_folder_names:
        if new_folder not in folders:
            print("Creating folder: {}".format(new_folder))
            os.mkdir(new_folder)
    return photo_folders

    
def move_photos(photo_folders):
    '''Takes a list of folders, copies the photos in the folders,
    and saves them to the newly created photos.
    '''
    for photo_folder in photo_folders:
        parts = photo_folder.split()
        if parts[0] in month_list:
            month = parts[0]
            month = convert_month_to_number(month)
            year = parts[-1]
            dest_folder = "{}-{}".format(year, month)
            files = os.listdir(photo_folder)
            print("Copying files from {} to {}...".format(photo_folder, dest_folder))
            for file in files:
                full_name = os.path.join(photo_folder, file)
                if(os.path.isfile(full_name)):
                    shutil.copy(full_name, dest_folder)
        else:
            for part in parts:
                if part in month_list:
                    month = part
                    month = convert_month_to_number(month)
                    year = parts[-1]
                    dest_folder = "{}-{}{}{}".format(year, month, sep, photo_folder)
                    try:
                        print('Copying folder {} to {}...'.format(photo_folder, dest_folder))
                        shutil.copytree(photo_folder, dest_folder)
                    except FileExistsError:
                        print("Duplicate files...doing nothing")
        
        
def get_exif_time(file_path):
    '''Takes a file path as input, extracts EXIF data, and returns the data
    '''
    img = open(file_path, 'rb')
    tags = exifread.process_file(img, details=False)
    try:
        timestamp = str(tags['EXIF DateTimeOriginal']).replace(':','-')
    except KeyError:
        try:
            timestamp = str(tags['EXIF DateTimeDigitized']).replace(':','-')
        except KeyError:
            print('Unable to find EXIF time. Leaving filename.')
            return
    return timestamp
    

def rename_files():
    '''Examines files in folders (that start with '20'), calls get_exif_time(), and renames the files to the EXIF time, if possible
    '''
    dirs = os.listdir()
    for dir in dirs:
        if dir.startswith('20'):
            for foldername, subfolders, filenames in os.walk(dir):
                print('Checking files in folder {}...'.format(foldername))
                for subfolder in subfolders:
                    print('Checking files in {} in {}...'.format(subfolder, foldername))
                for filename in filenames:
                    if not filename.startswith('20'):
                        print('Checking EXIF timestamp for {}...'.format(os.path.join(foldername, filename)))
                        file_path = os.path.join(foldername, filename)
                        new_name = get_exif_time(file_path)
                        print(new_name)
                        if new_name != None:
                            ext = filename.split('.')[-1]
                            new_name = "{}.{}".format(new_name, ext)
                            new_file_path = os.path.join(foldername, new_name)
                            try:
                                shutil.move(file_path, new_file_path)
                            except PermissionError as e:
                                print('Unable to rename file: {}'.format(file_path))
                                print(e)
                                continue


if __name__ == '__main__':                                
    if platform.system() == 'Windows':
        sep = '\\'
    else:
        sep = '/'
    folders = os.listdir()
    folder_names = []
    photo_folders = []
    month_list = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']

    pic_folders_to_move = setup_photos()
    move_photos(pic_folders_to_move)
    rename_files()