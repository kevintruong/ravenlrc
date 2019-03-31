"""
Helper methods for database
"""
import datetime
import sqlite3
import os
import uuid

curdir = os.path.abspath(os.path.dirname(__file__))
import abc


class LocalStorageDb(abc.ABC):
    def __init__(self, dbname):
        self.conn = self.connect(dbname)

    def connect(self, dbname):
        dbpath = os.path.join(curdir, dbname)
        return sqlite3.connect(dbpath,check_same_thread=False)

    @abc.abstractmethod
    def insert_file(self, metadata: dict):
        pass

    @abc.abstractmethod
    def create_schema(self):
        pass


class GdriveStorageDb(LocalStorageDb):
    FILES_TABLE = "tbl_files"

    def __init__(self, dbname):
        super().__init__(dbname)
        self.create_schema()

    def is_item_existed(self, metadata):
        items = self.get_info_by_id(metadata['id'])
        if len(items):
            return True
        else:
            return False

    def insert_file(self, metadata: dict):
        cursor = self.conn.cursor()
        cursor.execute('''
                INSERT or replace INTO tbl_files (
                    id,
                    name,
                    webContentLink,
                    mimeType,
                    modifiedTime
                ) VALUES (
                   ?,?,?,?,?
                );
                ''', (
            metadata["id"],
            metadata["name"],
            metadata["webContentLink"],
            metadata["mimeType"],
            metadata['modifiedTime']
        )
                       )
        self.conn.commit()
        cursor.close()
        return metadata["id"]

    def create_schema(self):
        cursor = self.conn.cursor()
        """
        tbl_files
            -> tbl_labels
            -> tbl_parentsCollection
            -> tbl_userPermission
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_files(
                id TEXT  PRIMARY KEY,
                name TEXT,
                webContentLink TEXT,
                mimeType TEXT,
                modifiedTime TEXT
            );
            ''')
        self.conn.commit()
        cursor.close()
        pass

    def select_all_files(self):
        """
        Generates a basic listing of files in tbl_files
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, id FROM tbl_files")
        files = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        return files

    def destroy(self):
        cursor = self.conn.cursor()
        cursor.execute("delete from tbl_files")
        cursor.close()
        self.conn.commit()

    def get_info_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_files WHERE id='{}'"
                       .format(id))
        iteminfo = cursor.fetchall()
        return iteminfo
        pass

    def search_info_by_key_value(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_files WHERE {}='{}'"
                       .format(key, value))
        iteminfo = cursor.fetchall()
        return iteminfo

    def list_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_files")
        iteminfo = cursor.fetchall()
        return iteminfo


import unittest


class Test_GdriveLocalDb(unittest.TestCase):
    def setUp(self) -> None:
        self.db = GdriveStorageDb('testdb.sqlite3')

    def test_insert_metadata(self):
        print('start')
        print('must None' + str(self.db.list_all()))
        id = str(uuid.uuid1())
        metadata = {
            'id': id,
            'name': 'this is the test',
            'webContentLink': 'http://helloworld',
            'mimeType': 'application/octet-stream',
            'modifiedTime': datetime.datetime.now().isoformat()
        }
        self.db.insert_file(metadata)
        print('has 1' + str(self.db.list_all()))
        metadata['modifiedTime'] = datetime.datetime.now().isoformat()
        self.db.insert_file(metadata)
        print('has 2' + str(self.db.list_all()))
        self.db.destroy()
        print('must None' + str(self.db.list_all()))

    def test_seach_by_key_value(self):
        info_items = self.db.search_info_by_key_value('name', 'this is the test')
        print(info_items)
