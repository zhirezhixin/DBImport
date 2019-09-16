# -*- coding: utf-8 -*-
"""Insert Data component.

This module gets lists of Course and Department objects from ReadCourseData.py
and insert those data into desired databse
"""


import os
from ReadCourseData import *
from configparser import ConfigParser
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger('DBImport_Logger')
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)   #get environmental variables


def get_db():
    """Get MongoDB username and password from .env file and returns desired databse.

    Args:
        'Mongo_User'(from '.env'): the user name used to access the mongoDB Atlas
        'Mongo_Password'(from '.env'): the password used to access the mongoDB Atlas
        'Mongo_DBName'(from '.env'): the desired database name
        'Mongo_Postfix'(from '.env'): the postfix of the srv link from MongoDB
    Raises:
        pymongo.errors: possibly connection errors or conficuration errors
    Returns:
        The database object

    """
    username, password = os.getenv('Mongo_User'), os.getenv('Mongo_Password')
    db_name = os.getenv('Mongo_DBName')
    client = MongoClient('mongodb+srv://' + username + ':' + password
                         + os.getenv('Mongo_Postfix'))
    return client.get_database(db_name)


def check_file_open(filename):
    """Check if the json file exist in the specific directory.

    Args:
        filename: the path to the desired file
    Raises:
        FileNotFoundError: Maybe try to find your file?
    Returns:
        The database object

    """
    if filename:
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        logging.info('File name: ', filename, ' cannot be found!')
        raise FileNotFoundError('File not found')


def insert_data(course_list, dept_list, quarter_name):
    """Insert data into databse.

    Get every single Course and Department object from the lists and 
    insert them into the correct database collections 
        (named quarter_name + 'course'/'departments')

    Args:
        course_list, dept_list: the lists of Course/Department objects
    Raises:
        pymongo.errors: possibly connection errors or conficuration errors
    Returns:
        None
 
    """
    db = get_db()
    course_collection = db[quarter_name + ' courses']
    dept_collection = db[quarter_name + ' departments']

    for course in course_list:
        temp_course = vars(course)
        course_collection.insert_one(temp_course)
    for dept in dept_list:
        temp_dept = vars(dept)
        dept_collection.insert_one(temp_dept)


def main():
    """Runner of this DBImport program.

    With help of other functions, this main function could read the data from
    json files and put them into desired databses.
    """
    logger.info('Excecution Started At: ', datetime.datetime.now())
    config = ConfigParser()
    config.read(os.getenv('Config_File_Name'))
    path = config['locations']['path']
    year = config['data_info']['start_year']

    try:
        while(config['locations'][str(year)]):
            all_quarters_in_year = config['locations'][str(year)].split(',')
            for each_quarter in all_quarters_in_year:
                quarter_name, filename = each_quarter[:-16].replace('_', ' '), path + each_quarter
                course_raw_data = check_file_open(filename)
                course_list, department_list = from_raw_to_list(course_raw_data, quarter_name)
                logger.info(datetime.datetime.now(),
                             ': Total loaded course for quarter ', each_quarter, ' ', len(course_list))
                insert_data(course_list, department_list, quarter_name)
            year += 1
    except Exception as e:
        logger.error(e)
        logger.info('Excecution Finished At: ', datetime.datetime.now())
        logger.basicConfig(filename='~/log_file.log', filemode='w', level=logging.DEBUG)


if __name__ == "__main__":
    main()
