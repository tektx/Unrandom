"""Unrandom Video Player

Creates a SQL table comprised of video files and their associated ratings.
A file's rating influences how often it is played.
"""

import collections
import csv
import os
import random

__author__ = 'Travis Knight'
__email__ = 'Travisknight@gmail.com'
__license__ = 'BSD'


def get_files(dirs_to_check, file_types):
    """ Get list of files that match the provided file types

    Args:
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


def rate_files(db_file):
    """ Prompts user for ratings of files in the database

    Args:
        db_file (str): Database file
    """
    # Read in files from the database
    ratings_dict = get_ratings_dict(db_file)

    # Prompt user to rate any unrated files
    for k, v in ratings_dict.items():
        rating = v
        # print('Rating for ' + k + ': ' + rating)
        if rating == '-1':
            prompt_string = 'Enter rating for ' + k + ': '
            new_rating = input(prompt_string)
            ratings_dict[k] = new_rating

    # Update database
    update_db(db_file, ratings_dict)


def update_db(db_file, ratings_dict):
    """ Updates the database file with a dictionary of files and ratings

    Args:
        db_file (str): Database file
        ratings_dict (dict): File paths as keys, values as ratings
    """
    print('Update database')
    with open(db_file, 'w', newline='') as outfile:
        wr = csv.writer(outfile)
        for k, v in ratings_dict.items():
            wr.writerow([k, v])


def get_ratings_dict(db_file):
    """ Creates a dictionary from a database file

    Args:
        db_file (str): Database file

    Returns:
        dict: File paths as keys, ratings as values
    """
    ratings_dict = {}
    try:
        with open(db_file, 'r') as infile:
            reader = csv.reader(infile)
            for k, v in reader:
                ratings_dict[k] = v
    except FileNotFoundError:
        print('No existing database found')
    return ratings_dict


def rating_to_select(db_file):
    """ Gets the rating of the file to play

    Get the adjusted count of all files, choose a random number in that range, and return the appropriate rating.
    Example:
        Given 100 files of rating 1, 20 files of rating 2, and 10 files of rating 3
        Rating 1 has weight 1, rating 2 has weight 4, rating 3 has weight 16
        (100*1) + (20*4) + (10*16) = 340
        Random number is chosen between 1-340
        If number is 1<=100, '1' is returned
        If number is 101<=180, '2' is returned
        Else rating '3' is returned

    Args:
        db_file (str): Database file

    Returns:
        str: Rating to use
    """
    weights = collections.OrderedDict()
    weights['1'] = 1
    weights['2'] = 4
    weights['3'] = 16
    rating_counts = collections.OrderedDict()
    for k in weights.keys():
        rating_counts[k] = 0
    ratings_dict = get_ratings_dict(db_file)
    adjusted_count = 0
    for k, v in ratings_dict.items():
        try:
            count_to_add = weights[v]
            rating_counts[v] = rating_counts[v] + count_to_add
            adjusted_count = adjusted_count + count_to_add
        except KeyError:
            pass
    print('Adjusted count: ' + str(adjusted_count))

    # Generate a random number to determine the rating level of the file to open
    random_number = random.randrange(1, adjusted_count)
    count = 0
    for k, v in rating_counts.items():
        count = count + v
        if random_number <= count:
            print('Open file with rating ' + k)
            return k
    raise Exception('Random number was not in the expected range')


def open_file(db_file):
    """ Opens a file from the ratings database

    Args:
        db_file (str): Database file
    """
    selected_rating = rating_to_select(db_file)
    ratings_dict = get_ratings_dict(db_file)
    files_to_choose_from = [k for k, v in ratings_dict.items() if v == selected_rating]
    files_length = len(files_to_choose_from)
    random_number = random.randint(0, files_length-1)
    file_to_open = files_to_choose_from[random_number]
    print('\n' + 'Rating ' + selected_rating + ': ' + file_to_open)
    try:
        os.system('start "" "' + file_to_open + '"')
    except FileNotFoundError:
        print('Error: File ' + file_to_open + ' not found!')

    # Loop back to main selection so a new file can be opened.
    main()


def create_db(db_file, dirs_to_check, file_types):
    """ Creates the database of files and ratings

    Args:
        db_file (str): Database file
        dirs_to_check (list[str]): Paths of the directories to check for files
        file_types (tuple[str]): File types to add to the database
    """
    files = get_files(dirs_to_check, file_types)

    # Create a dictionary of the found files
    new_ratings_dict = {}
    for f in files:
        print(f)
        new_ratings_dict[f] = '-1'

    # Import existing database into a dictionary
    old_ratings_dict = get_ratings_dict(db_file)

    # Merge the old database into the new one
    new_ratings_dict.update(old_ratings_dict)

    # Create a CSV file with the new dictionary
    update_db(db_file, new_ratings_dict)


def main():
    """ Lists options for user

    :return:
    """
    db_name = 'Unrandom_db'
    dirs_to_check = [os.getcwd()]
    file_types = ('.avi', '.wmv', '.mkv', '.mp4')
    db_file = db_name + '.csv'

    choice = input('1) Build ratings database\n'
                   '2) Rate files\n'
                   '3) Open random file\n')

    if choice == '1':
        create_db(db_file, dirs_to_check, file_types)
    elif choice == '2':
        rate_files(db_file)
    elif choice == '3':
        open_file(db_file)
    else:
        print('Invalid choice')
        main()

if __name__ == '__main__':
    main()
