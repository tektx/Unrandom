""" Unrandom Video Player

    This script creates a SQL table comprised of video files and their associated ratings
    A file's rating influences how often it is played in a pseudo-random fashion
    A file with a 0 rating is not played randomly
    A file with a 1 rating is played 1/21 times
    A file with a 2 rating is played 4/21 times
    A file with a 3 rating is played 16/21 times
"""

__author__ = 'tektx'

import pymysql as db
import os
import sys
import string
import array
import random

DB_CONN = db.connect(user='root', password='password', database='ratings')
CURSOR = DB_CONN.cursor()
CUR_DIR = os.getcwd()
FOLDER = os.path.relpath(".", "..")
PUNCTUATION = '''!()-[]{};:'"\,<>. /?@#$%^&*_~'''
file_list = []


def list_files():
    for root, dirs, files in os.walk(CUR_DIR):
        for file_name in files:
            if file_name.endswith((".avi", ".wmv", ".mkv", ".mp4")):
                # print(os.path.abspath(file_name))
                file_list.append(root + "\\" + file_name)


def random_rating():
    two_weight = 4
    three_weight = 4
    max_range = 1 + two_weight + three_weight*two_weight
    random_num = random.randrange(1, max_range)
    print("Range: 1-" + str(max_range) + ": " + str(random_num))
    if random_num == 1:
        return 1
    elif random_num <= two_weight+1:
        return 2
    else:
        return 3


def main():
    list_files()
    folder_name = ""
    for char in FOLDER:
        if char not in PUNCTUATION:
            folder_name += char.lower()

    choice = input("1) Build ratings database, 2) Rate files, 3) Open random file")

    if choice == "1":
        print("Building database")
        CURSOR.execute("SHOW TABLES LIKE '" + folder_name + "';")
        if CURSOR.fetchone():
            print("Table exists")
        else:
            CURSOR.execute("CREATE TABLE IF NOT EXISTS " + folder_name + " (id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY, "
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
        # print("Rating: " + str(random_rating()))
        CURSOR.execute("SELECT filepath FROM " + folder_name + " WHERE rating = " + str(random_rating()) + ";")
        files = CURSOR.fetchall()
        selection_length = len(files)
        selected_file = files[random.randrange(0, selection_length-1)][0]
        print(selected_file)
        os.startfile(selected_file)

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
