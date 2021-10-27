import pickle
import os
import sqlite3
import json
import re

# filepath = './pickled_cookies/1310107654071838_post-accept_www_gov_uk.pkl'

# cookies = pickle.load(open(filepath, "rb"))
# for cookie in cookies:
#     print(cookie)

### Too tired to finish this, will be done for tomorrow... Sorry :( ###

PICKLE_DIR_PATH = './pickled_cookies'
CREATE_COOKIE_TABLE = '''
    CREATE TABLE IF NOT EXISTS cookies 
    (access_date LONG, hash TEXT, stage TEXT, original_url TEXT, visit_id LONG, domain TEXT, expiry LONG, http_only BOOL, name TEXT, path TEXT, same_site TEXT, secure BOOL, value TEXT)
'''

INSERT_INTO_COOKIE_TABLE = '''
    INSERT INTO cookies 
        (access_date, hash, stage, original_url, visit_id, domain, expiry, http_only, name, path, same_site, secure, value) VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''

def connect_to_db(db_name='unpickled.sqlite'):
    db_path = './outp/{}'.format(db_name)
    if not os.path.exists(db_path):
        os.makedirs('./outp')
        with open(db_path, 'w'): pass

    connection = sqlite3.connect(db_path)
    return connection


def init_db_tables(db_connection):
    db_cursor = db_connection.cursor()
    db_cursor.execute(CREATE_COOKIE_TABLE)
    db_connection.commit()


def get_value_or_null(dict, key):
    if key not in dict:
        return 'NULL'
    return dict[key]


def unpickle_cookies(db_connection):
    db_cursor = db_connection.cursor()
    pickle_files = os.listdir(PICKLE_DIR_PATH)
    for pickle_file in pickle_files:
        cookies = pickle.load(open('{}/{}'.format(PICKLE_DIR_PATH, pickle_file), 'rb'))
        for cookie in cookies:
            openwpm_cookie = cookie['openwpm_cookie']
            db_cursor.execute(INSERT_INTO_COOKIE_TABLE, (cookie['access_date'], cookie['cookie_hash'], cookie['stage'], cookie['original_url'], cookie['visit_id'],
                get_value_or_null(openwpm_cookie, 'domain'), get_value_or_null(openwpm_cookie, 'expiry'), get_value_or_null(openwpm_cookie, 'httpOnly'), 
                get_value_or_null(openwpm_cookie, 'name'), get_value_or_null(openwpm_cookie, 'path'), get_value_or_null(openwpm_cookie, 'sameSite'), 
                get_value_or_null(openwpm_cookie, 'secure'), get_value_or_null(openwpm_cookie, 'value')))
            db_connection.commit()


def main():
    db_connection = connect_to_db()
    init_db_tables(db_connection)
    unpickle_cookies(db_connection)
    db_connection.close()


if __name__ == '__main__':
    main()