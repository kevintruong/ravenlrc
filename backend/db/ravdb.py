from threading import Thread

import psycopg2
from psycopg2 import sql

# USERNAME = "postgres"
# DBNAME = 'ravdb'
# PASSWORD = 'kevinelg'
# HOST_URL = '172.17.0.2'

USERNAME = "ravtech"
DBNAME = 'ravdb'
PASSWORD = '*utG!~ue$k~Wb63'
HOST_URL = '54.169.147.105'


class RavDataBase:
    def __init__(self):
        self.conn = None

    def connect(self):
        posgres_url = 'postgres://{}:{}@{}/{}'.format(USERNAME, PASSWORD, HOST_URL, DBNAME)
        self.conn = psycopg2.connect(posgres_url)

    def close(self):
        if self.conn:
            self.conn.close()

    def destroy(self, tb_name: str):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("delete from {}".format(tb_name))
            cursor.close()
            self.conn.commit()
        finally:
            self.close()


class RavSongDb(RavDataBase):
    def __init__(self):
        super().__init__()
        self.create_schema()

    def create_schema(self):
        try:
            self.connect()
            cur = self.conn.cursor()
            cur.execute('\n'
                        '                CREATE TABLE IF NOT EXISTS songs_info(\n'
                        '                    id text  PRIMARY KEY,\n'
                        '                    singer text,\n'
                        '                    title text,\n'
                        '                    songfile text,\n'
                        '                    lyrictext text,\n'
                        '                    lyric text,\n'
                        '                    info text,\n'
                        '                    timelength INTEGER \n'
                        '                );\n'
                        '                ')
            cur.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

    def get_info_by_id(self, id):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM songs_info WHERE id='{}'"
                           .format(id))
            iteminfo = cursor.fetchone()
            return iteminfo
        finally:
            if self.conn is not None:
                self.conn.close()

    def search_info_by_key_value(self, key, value):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM songs_info WHERE {}='{}'"
                           .format(key, value))
            iteminfo = cursor.fetchall()
            return iteminfo
        finally:
            if self.conn is not None:
                self.conn.close()

    def list_all(self):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM songs_info")
            iteminfo = cursor.fetchall()
            return iteminfo
        finally:
            if self.conn is not None:
                self.conn.close()

    def insert_song(self, metadata: dict):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql.SQL("INSERT INTO {}  VALUES ( %s,%s,%s,%s,%s,%s,%s,%s) \
                                    ON CONFLICT(id) \
                                    DO NOTHING").format(sql.Identifier('songs_info')),
                           [
                               metadata["id"],
                               metadata["singer"],
                               metadata["title"],
                               metadata["songfile"],
                               metadata['lyrictext'],
                               metadata['lyric'],
                               metadata['info'],
                               metadata['timeleng']]
                           )
            cursor.close()
            self.conn.commit()
            return metadata["id"]
        finally:
            if self.conn is not None:
                self.conn.close()

    def destroy(self):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("delete from songs_info")
            cursor.close()
            self.conn.commit()
        finally:
            if self.conn is not None:
                self.conn.close()


class UpdateThread(Thread):
    def __init__(self, songinfo):
        super().__init__()
        from backend.type import SongInfo
        self.songinfo: SongInfo = songinfo
        self.start()

    def run(self) -> None:
        songinfo = self.songinfo
        from backend.storage.content import CachedContentDir
        from backend.utility.Utility import get_media_info
        songitem = RavSongDb().get_info_by_id(songinfo.id)
        filepath = None
        if songitem is None:
            try:
                filepath = CachedContentDir.GdriveCacheStorage.download_file(songinfo.songfile)
                timelength = get_media_info(filepath)
                songinfo.timeleng = timelength
                record = songinfo.__dict__
                RavSongDb().insert_song(record)
            finally:
                import os
                if filepath:
                    os.remove(filepath)


#
# import unittest
#
#
# class Test_GdriveSongDb(unittest.TestCase):
#     def setUp(self) -> None:
#         self.db = RavSongDb()
#
#     def test_insert_metadata(self):
#         print('start')
#         self.db.destroy()
#         print('must None' + str(self.db.list_all()))
#         import uuid
#         id = str(uuid.uuid1())
#         metadata = {
#             'id': id,
#             'singer': "kevinelg",
#             'title': "kevin",
#             'songfile': 'songfile.mp3',
#             'lyrictext': "lyric text",
#             'lyric': "lyric.lrc",
#             'info': 'songinfo',
#             'timeleng': 15000
#         }
#         self.db.insert_song(metadata)
#         print('has {}'.format(len(self.db.list_all())))
#         metadata['id'] = 'test'
#         self.db.insert_song(metadata)
#         print('has {}'.format(len(self.db.list_all())))
#         self.db.insert_song(metadata)
#         print('has {}'.format(len(self.db.list_all())))
#         print('must None' + str(self.db.list_all()))
#         self.db.destroy()
#         print('must None' + str(self.db.list_all()))
#
#     def test_migrate_data_from_sqlite_to_postgres(self):
#         pass


if __name__ == '__main__':
    from crawler.db.helper import GdriveSongInfoDb
    from backend.type import SongInfo

    songdb = GdriveSongInfoDb.get_gdrivesonginfodb()
    infos = songdb.list_all()
    for songitem in infos:
        filepath = None
        songinfo = SongInfo(songitem)
        thread = UpdateThread(songinfo)
        thread.join()
        # break
