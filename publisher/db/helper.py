"""
Helper methods for database
"""

import sqlite3
import os


def connect():
    dbpath = os.getenv("HOME") + os.path.sep + ".gdrive-cli.db"
    return sqlite3.connect(dbpath)


"""
Inserts file metadata returned by gdrive.insert_file into the
tbl_files table and tables related to it.

Returns:
    id of the inserted data
"""


def insert_account(accinfo):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_accounts (
            useraccount,
            password,
            token
        ) VALUES (
           ?,?,?
        );
        """, (
        accinfo["useraccount"],
        accinfo["password"],
        accinfo["token"],
    ))
    conn.commit()
    cursor.close()


def insert_info(pageinfo):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tbl_pages 
        (
            id,
            name,
            token,
        ) VALUES (
            ?,?,?
        );
        """, (
        pageinfo["id"],
        pageinfo["name"],
        pageinfo["token"],
    ))
    conn.commit()
    cursor.close()

    return pageinfo["id"]


def select_all_files():
    """
    Generates a basic listing of files in tbl_files
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT title, id FROM tbl_files")
    files = cursor.fetchall()
    cursor.close()
    conn.commit()

    return files
