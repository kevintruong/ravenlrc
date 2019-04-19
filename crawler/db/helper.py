"""
Helper methods for database
"""
import datetime
import sqlite3
import os
import uuid

from config.configure import BackendConfigure
config: BackendConfigure = BackendConfigure.get_config()
curdir = config.get_config().TmpDir
import abc


class SongInfoDb(abc.ABC):
    def __init__(self, dbname):
        self.conn = self.connect(dbname)

    def connect(self, dbname):
        dbpath = os.path.join(curdir, dbname)
        return sqlite3.connect(dbname, check_same_thread=False)

    @abc.abstractmethod
    def insert_song(self, metadata: dict):
        pass

    @abc.abstractmethod
    def create_schema(self):
        pass


class GdriveSongInfoDb(SongInfoDb):
    FILES_TABLE = "tbl_songs"

    def __init__(self, dbname):
        super().__init__(dbname)
        self.create_schema()

    def is_item_existed(self, metadata):
        items = self.get_info_by_id(metadata['id'])
        if len(items):
            return True
        else:
            return False

    def insert_song(self, metadata: dict):
        cursor = self.conn.cursor()
        cursor.execute('''
                INSERT or replace INTO tbl_songs (
                    id,
                    singer,
                    title,
                    songfile,
                    lyrictext,
                    lyric,
                    info
                ) VALUES (
                   ?,?,?,?,?,?,?
                );
                ''', (
            metadata["id"],
            metadata["singer"],
            metadata["title"],
            metadata["songfile"],
            metadata['lyrictext'],
            metadata['lyric'],
            metadata['info']
        )
                       )
        self.conn.commit()
        cursor.close()
        return metadata["id"]

    def create_schema(self):
        cursor = self.conn.cursor()
        """
        tbl_files
            -> tbl_songs
            id : nct_id
            singer: singer name 
            title: song_title
            songfile: URI (ID of google drive)
            lyrictext : full text of lyric 
            lyric: URI (ID of google drive lyric file)
            info: 'url'
        """
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_songs(
                id TEXT  PRIMARY KEY,
                singer TEXT,
                title TEXT,
                songfile TEXT,
                lyrictext TEXT,
                lyric TEXT,
                info TEXT
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
        cursor.execute("SELECT title, id FROM tbl_songs")
        files = cursor.fetchall()
        cursor.close()
        self.conn.commit()
        return files

    def destroy(self):
        cursor = self.conn.cursor()
        cursor.execute("delete from tbl_songs")
        cursor.close()
        self.conn.commit()

    def get_info_by_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_songs WHERE id='{}'"
                       .format(id))
        iteminfo = cursor.fetchall()
        return iteminfo
        pass

    def search_info_by_key_value(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_songs WHERE {}='{}'"
                       .format(key, value))
        iteminfo = cursor.fetchall()
        return iteminfo

    def list_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tbl_songs")
        iteminfo = cursor.fetchall()
        return iteminfo


import unittest


class Test_GdriveSongDb(unittest.TestCase):
    def setUp(self) -> None:
        self.db = GdriveSongInfoDb('testdb.sqlite3')

    def test_insert_metadata(self):
        print('start')
        print('must None' + str(self.db.list_all()))
        id = str(uuid.uuid1())
        metadata = {
            'id': id,
            'singer': "kevinelg",
            'title': "kevinelg",
            'songfile': 'songfile.mp3',
            'lyrictext': "lyric text",
            'lyric': "lyric_file.lrc",
            'info': 'songinfo'
        }
        self.db.insert_song(metadata)
        print('has {}'.format(len(self.db.list_all())))
        metadata['id'] = 'test'
        self.db.insert_song(metadata)
        print('has {}'.format(len(self.db.list_all())))
        self.db.insert_song(metadata)
        print('has {}'.format(len(self.db.list_all())))
        self.db.destroy()
        print('must None' + str(self.db.list_all()))

    def test_seach_by_key_value(self):
        info_items = self.db.search_info_by_key_value('name', 'this is the test')
        print(info_items)
