"""Unrandom Video Player

Creates a SQL table comprised of video files and their associated ratings.
A file's rating influences how often it is played.
"""

import csv
import pymysql
import os
import random

__author__ = 'Travis Knight'
__email__ = 'Travisknight@gmail.com'
__license__ = 'BSD'

DB_CONN = pymysql.connect(user='root', password='password', database='ratings')
CURSOR = DB_CONN.cursor()
CUR_DIR = os.getcwd()
REL_DIR = os.path.relpath('.', '..')
PUNCTUATION = '''!()-[]{};:'"\,<>. /?@#$%^&*_~'''
# TYPE_AUDIO = ('.mp3')


def get_files(dirs_to_check, file_types):
    """ Get list of files that match the provided file types

    Parameters:
        dirs_to_check (list[str]): Directories to check for files
        file_types (tuple[str]): File types to include in the return list

    Returns:
        list[str]: Files of the provided types in all subdirectories of the provided directory
    """
    files_to_add = []
    for dir_to_check in dirs_to_check:
        for root, dirs, files in os.walk(dir_to_check):
            for file_name in files:
                if file_name.endswith(file_types):
                    # print(os.path.abspath(file_name))
                    files_to_add.append(root + '\\' + file_name)
    return files_to_add


def get_adjusted_count(folder_name):
    # User-provided values to determine the weight of higher ratings
    # Default: File rated 2 is selected 4x as often as a file rated 1; file rated 3 is selected 4x as often as a 2
    two_weight = 4
    three_weight = 4

    CURSOR.execute('SELECT COUNT(*) FROM ' + folder_name + ' WHERE rating = 1')
    file_count_ones = CURSOR.fetchone()[0]
    CURSOR.execute('SELECT COUNT(*) FROM ' + folder_name + ' WHERE rating = 2')
    file_count_twos = file_count_ones + CURSOR.fetchone()[0]*two_weight
    CURSOR.execute('SELECT COUNT(*) FROM ' + folder_name + ' WHERE rating = 3')
    file_count_threes = file_count_twos + CURSOR.fetchone()[0]*two_weight*three_weight
    # Generate a random number to determine the rating level of the file to open
    random_number = random.randrange(1, file_count_threes)
    if random_number <= file_count_ones:
        return '1'
    elif random_number <= file_count_twos:
        return '2'
    else:
        return '3'


def build_db(folder):
    print('Building database')
    CURSOR.execute("SHOW TABLES LIKE '" + folder + "';")
    if CURSOR.fetchone():
        print('Table exists')
    else:
        CURSOR.execute('CREATE TABLE IF NOT EXISTS ' + folder +
                       '(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, '
                       'rating INT(1) UNSIGNED, '
                       'filepath VARCHAR(500) NOT NULL UNIQUE,'
                       'filename VARCHAR(500) NOT NULL);')
    for file in file_list:
        print('Adding ' + file)
        file_escaped = file.replace('\\', '\\\\')
        filename_only = file.rsplit('\\', 1)[1]
        # print(filename_only)
        CURSOR.execute('INSERT INTO ' + folder + ' (id, rating, filepath, filename) VALUES (NULL, 9, \"' +
                       file_escaped + '\", \"' + filename_only + '\") ON DUPLICATE KEY UPDATE id=id;')
    CURSOR.execute('COMMIT;')


def rate(folder):
    CURSOR.execute('SELECT filename from ' + folder + ' WHERE rating = 9;')
    unrated_file = CURSOR.fetchall()
    i = 0
    while i < len(unrated_file):
        new_rating = input('Enter rating for ' + unrated_file[i][0])
        CURSOR.execute('UPDATE ' + folder + ' SET rating = ' + new_rating +
                       ' WHERE filename = \"' + unrated_file[i][0] + '\";')
        CURSOR.execute('COMMIT;')
        i += 1


def open_file(folder):
    selected_rating = get_adjusted_count(folder)
    CURSOR.execute('SELECT filepath FROM ' + folder + ' WHERE rating = ' + selected_rating + ';')
    files = CURSOR.fetchall()
    files_length = len(files)
    selected_file = files[random.randrange(0, files_length-1)][0]
    print('SELECTED FILE: ' + selected_file)
    # CURSOR.execute('SELECT filename FROM ' + folder + ' WHERE filepath LIKE ' + selected_file + ';')
    # selected_filename = CURSOR.fetchone()[0]
    print('\n' + 'Rating ' + selected_rating + ': ' + selected_file)
    os.startfile(selected_file)

    # Loop back to main selection so a new file can be opened.
    main()


def create_db(db_name, dirs_to_check, file_types):
    """ Creates the database of files and ratings

    Parameters:
        db_name (str): Name of the database file
        dirs_to_check (list[str]): Paths of the directories to check for files
        file_types (tuple[str]): File types to add to the database
    """
    db_file = db_name + '.csv'
    files = get_files(dirs_to_check, file_types)

    # Create a dictionary of the found files
    new_ratings_dict = {}
    for f in files:
        print(f)
        new_ratings_dict[f] = '-1'

    # Import existing database into a dictionary
    old_ratings_dict = {}
    try:
        with open(db_file, 'r') as infile:
            reader = csv.reader(infile)
            for k, v in reader:
                old_ratings_dict[k] = v
    except FileNotFoundError:
        print('No existing database found')

    # Merge the old database into the new one
    new_ratings_dict.update(old_ratings_dict)

    # Create a CSV file with the new dictionary
    print('Create database')
    with open(db_file, 'w', newline='') as outfile:
        wr = csv.writer(outfile)
        for k, v in new_ratings_dict.items():
            wr.writerow([k, v])


def main():
    """ Lists options for user

    :return:
    """
    db_name = 'Unrandom_db'
    dirs_to_check = [os.getcwd()]
    file_types = ('.avi', '.wmv', '.mkv', '.mp4')
    folder = ''
    for char in REL_DIR:
        if char not in PUNCTUATION:
            folder += char.lower()

    choice = input('1) Build ratings database\n'
                   '2) Rate files\n'
                   '3) Open random file\n')

    if choice == '1':
        create_db(db_name, dirs_to_check, file_types)
    elif choice == '2':
        rate(folder)
    elif choice == '3':
        open_file(folder)
    else:
        print('Invalid choice')
        main()

if __name__ == '__main__':
    main()
