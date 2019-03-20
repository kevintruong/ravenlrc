import os
import sqlite3

DEFAULT_DB = os.path.join(os.path.dirname(__file__), 'authenticate.sqlite3')


class YtServiceAuthentication:
    def __init__(self, channel):
        self.google_secretkey = None
        self.ytcredentialfile = None


class FbFanPageAuthentication:
    def __init__(self, channel):
        self.fb_token = None
        self.pageid = None
        pass


class AuthenticateManger:
    AuthenticateTableName = r'ServiceAuthenticateDb'

    def __init__(self, channel: str):
        self.create_authenticatedb()
        self.yt_auth = YtServiceAuthentication(channel)
        self.fb_auth = FbFanPageAuthentication(channel)

    def create_authenticatedb(self):
        self.dbfile = DEFAULT_DB
        self.debugdbconn = sqlite3.connect(self.dbfile)
        sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS {} (
                                            channel integer primary key ,
                                            type text,
                                            google_secretkey text ,
                                            channel_credential text  ,
                                            fbtoken text 
                                            pageid text
                                        );""".format(self.AuthenticateTableName)
        cur = self.debugdbconn.cursor()
        cur.execute(sql_create_tasks_table)
        self.debugdbconn.commit()

    def get_channel_yt_auth(self):
        return self.get_channel_yt_auth()
        pass

    def get_channel_fbpage_auth(self):
        return self.get_channel_fbpage_auth()

    def add_new_channel_auth(self, channel, callback=None):
        from backend.publisher.youtube.youtube_uploader import YoutubeUploader
        YoutubeUploader(channel, callback)

        pass
        #         TODO
        #   add process to create a new channel authenticate. include FB and Yt
        # include youtube get youtube credential file + facebook access page token + page id


import unittest


class Test_Authenticatemanager(unittest.TestCase):

    def test_create_authenticatedb(self):
        pass
