""" Unrandom Video Player

    This script creates a SQL table comprised of video files and their associated ratings
    A file's rating influences how often it is played in a pseudo-random fashion

    To Do:
    Check if a file no longer exists.
"""

__author__ = 'tektx'

import pymysql
import os
import random

DB_CONN = pymysql.connect(user='root', password='password', database='ratings')
CURSOR = DB_CONN.cursor()
CUR_DIR = os.getcwd()
FOLDER = os.path.relpath(".", "..")
PUNCTUATION = '''!()-[]{};:'"\,<>. /?@#$%^&*_~'''
TYPE_VIDEO = (".avi", ".wmv", ".mkv", ".mp4")
# TYPE_AUDIO = (".mp3")
file_list = []


def list_files():
    for root, dirs, files in os.walk(CUR_DIR):
        for file_name in files:
            if file_name.endswith(TYPE_VIDEO):
                # print(os.path.abspath(file_name))
                file_list.append(root + "\\" + file_name)


def get_adjusted_count(folder_name):
    # User-provided values to determine the weight of higher ratings
    # Default: File rated 2 is selected 4x as often as a file rated 1; file rated 3 is selected 4x as often as a 2
    two_weight = 4
    three_weight = 4

    CURSOR.execute("SELECT COUNT(*) FROM " + folder_name + " WHERE rating = 1")
    file_count_ones = CURSOR.fetchone()[0]
    CURSOR.execute("SELECT COUNT(*) FROM " + folder_name + " WHERE rating = 2")
    file_count_twos = file_count_ones + CURSOR.fetchone()[0]*two_weight
    CURSOR.execute("SELECT COUNT(*) FROM " + folder_name + " WHERE rating = 3")
    file_count_threes = file_count_twos + CURSOR.fetchone()[0]*two_weight*three_weight
    # Generate a random number to determine the rating level of the file to open
    random_number = random.randrange(1, file_count_threes)
    if random_number <= file_count_ones:
        return "1"
    elif random_number <= file_count_twos:
        return "2"
    else:
        return "3"


def main():
    list_files()
    folder_name = ""
    for char in FOLDER:
        if char not in PUNCTUATION:
            folder_name += char.lower()

    choice = input("1) Build ratings database\n2) Rate files\n3) Open random file\n")

    if choice == "1":
        print("Building database")
        CURSOR.execute("SHOW TABLES LIKE '" + folder_name + "';")
        if CURSOR.fetchone():
            print("Table exists")
        else:
            CURSOR.execute("CREATE TABLE IF NOT EXISTS " + folder_name +
                           "(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, "
                           "rating INT(1) UNSIGNED, "
                           "filepath VARCHAR(500) NOT NULL UNIQUE,"
                           "filename VARCHAR(500) NOT NULL);")
        for file in file_list:
            print("Adding " + file)
            file_escaped = file.replace('\\', '\\\\')
            filename_only = file.rsplit('\\', 1)[1]
            # print(filename_only)
            CURSOR.execute("INSERT INTO " + folder_name + " (id, rating, filepath, filename) VALUES (NULL, 9, \"" +
                           file_escaped + "\", \"" + filename_only + "\") ON DUPLICATE KEY UPDATE id=id;")
        CURSOR.execute("COMMIT;")

    elif choice == "2":
        CURSOR.execute("SELECT filename from " + folder_name + " WHERE rating = 9;")
        unrated_file = CURSOR.fetchall()
        i = 0
        while i < len(unrated_file):
            new_rating = input("Enter rating for " + unrated_file[i][0])
            CURSOR.execute("UPDATE " + folder_name + " SET rating = " + new_rating +
                           " WHERE filename = \"" + unrated_file[i][0] + "\";")
            CURSOR.execute("COMMIT;")
            i += 1

    elif choice == "3":
        selected_rating = get_adjusted_count(folder_name)
        CURSOR.execute("SELECT filepath FROM " + folder_name + " WHERE rating = " + selected_rating + ";")
        files = CURSOR.fetchall()
        files_length = len(files)
        selected_file = files[random.randrange(0, files_length-1)][0]
        # CURSOR.execute("SELECT filename FROM " + folder_name + " WHERE filepath LIKE " + selected_file + ";")
        # selected_filename = CURSOR.fetchone()[0]
        print('\n' + "Rating " + selected_rating + ": " + selected_file)
        os.startfile(selected_file)

        # Loop back to main selection so a new file can be opened without rerunning the script.
        main()

    else:
        print("Invalid choice")
        main()

if __name__ == "__main__":
    main()
