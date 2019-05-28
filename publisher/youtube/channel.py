import json
import os

import psycopg2
from psycopg2 import sql

from backend.storage.content import ContentDir
from config.configure import BackendConfigure
from backend.db.ravdb import RavDataBase
from publisher.youtube import auth


class ChannelInfo:
    def __init__(self, channel_name, fid):
        self.channel = channel_name
        self.token_fid = fid

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)


class YtChannelDb(RavDataBase):
    tb_name = 'yt_channel_info_tb'

    def __init__(self):
        super().__init__()

    def create_schema(self):
        try:
            self.connect()
            cur = self.conn.cursor()
            cur.execute('\n'
                        '                CREATE TABLE IF NOT EXISTS {}(\n'
                        '                    channel text  PRIMARY KEY,\n'
                        '                    token_fid text\n'
                        '                );\n'
                        '                '.format(self.tb_name))
            cur.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            raise error
        finally:
            self.close()

    def insert_channel_info(self, channel_info: ChannelInfo):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql.SQL("INSERT INTO {}(channel,token_fid) \
                                    VALUES {} \
                                    ON CONFLICT(channel) \
                                        DO  UPDATE SET \
                                        token_fid = EXCLUDED.token_fid;".format(self.tb_name,
                                                                                (channel_info.channel,
                                                                                 channel_info.token_fid))
                                   )
                           )
            cursor.close()
            self.conn.commit()
        except Exception as exp:
            from backend.yclogger import stacklogger, slacklog
            print(stacklogger.format(exp))
            slacklog.error(stacklogger.format(exp))
        finally:
            self.close()
            pass

    def get_acc_info_by_name(self, name):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {} \
                            WHERE channel='{}'".format(self.tb_name, name))
            iteminfo = cursor.fetchone()
            if iteminfo:
                return ChannelInfo(iteminfo[0], iteminfo[1])
            return None
        finally:
            self.close()

    def list_all_page_info(self):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {}".format(self.tb_name))
            iteminfo = cursor.fetchall()
            if iteminfo:
                listchannel = []
                for each_item in iteminfo:
                    info = ChannelInfo(each_item[0], each_item[1])
                    listchannel.append(info)
                return listchannel
            return None
        finally:
            self.close()


class YoutubeChannelHandler:
    CurDir = os.path.dirname(os.path.realpath(__file__))
    AuthenticateFileDir = os.path.join(CurDir, '../auth')

    def __init__(self, channel=None):
        self.channel = channel
        self.credential_file = None
        self.resource = None
        pass

    @classmethod
    def get_secret_file(cls):
        return os.path.join(cls.AuthenticateFileDir, 'client_secrets.json')

    def get_token_file(self):
        pageinfo = YtChannelDb().get_acc_info_by_name(self.channel)
        token_file = os.path.join(ContentDir.CHANNELINFO_DIR, "{}.json".format(self.channel))
        if pageinfo:
            with open(token_file, 'w') as filefd:
                filefd.write(pageinfo.token_fid)
            return token_file
        return token_file

    def update_channel_info(self, credentifile):
        if not os.path.exists(credentifile):
            raise FileExistsError('{} not found'.format(credentifile))
        with open(credentifile, 'r') as crefile:
            crendentialdata = crefile.read()
        channelinfo = ChannelInfo(self.channel, crendentialdata)
        YtChannelDb().insert_channel_info(channelinfo)

    def auth_new_channel(self, callback):
        from backend.utility.TempFileMnger import JsonCredentialTempFile
        tokenfile = JsonCredentialTempFile().getfullpath()
        try:
            default_credentials = tokenfile
            credentials = default_credentials
            client_secrets = self.get_secret_file()
            if callback is None:
                from publisher.youtube.auth import console
                get_code_callback = console.get_code
            else:
                get_code_callback = callback
            self.resource = auth.get_resource(client_secrets,
                                              credentials,
                                              get_code_callback=get_code_callback)
            self.credential_file = credentials
        except Exception as exp:
            print(exp)
            raise exp

    def add_new_channel(self, callback=None):
        self.auth_new_channel(callback)
        self.channel = self.get_channel_name()
        self.update_channel_info(self.credential_file)

    def get_channel_name(self):
        request = self.resource.channels().list(
            part="snippet",
            mine=True
        )
        response = request.execute()
        if len(response['items']):
            info = response['items'][0]
            id = info['id']
            name = info['snippet']['title']
            return name
        else:
            return None

    def auth_confirm(self, url):
        import webbrowser
        webbrowser.open(url, new=2)
        return input('input token')

    def get_youtube_handler(self, callback=None):
        """
            Return
            the
            API
            Youtube
            object.
            """
        try:
            default_credentials = self.get_token_file()
            client_secrets = self.get_secret_file()
            credentials = default_credentials
            if callback is None:
                from publisher.youtube.auth import console
                get_code_callback = console.get_code
            else:
                get_code_callback = callback
            self.resource = auth.get_resource(client_secrets,
                                              credentials,
                                              get_code_callback=get_code_callback)
            self.update_channel_info(credentials)
            return self.resource
        except Exception as exp:
            print(exp)
            raise exp


import unittest


class Test_YtChannelInfoDb(unittest.TestCase):
    def setUp(self) -> None:
        self.channel = ChannelInfo('kevintruong', '123456')

    def test_inser_channelinfo(self):
        YtChannelDb().insert_channel_info(self.channel)
        channelinfo = YtChannelDb().get_acc_info_by_name(self.channel.channel)
        self.assertIsNotNone(channelinfo)
        self.channel.token_fid = 'kevintruong'
        YtChannelDb().insert_channel_info(self.channel)
        channelinfo = YtChannelDb().get_acc_info_by_name(self.channel.channel)
        self.assertIsNotNone(channelinfo)
        print(channelinfo.token_fid)
        self.channel.channel = 'thienhanh'
        YtChannelDb().insert_channel_info(self.channel)
        channelinfo = YtChannelDb().get_acc_info_by_name(self.channel.channel)
        print(channelinfo.toJSON())
        self.assertIsNotNone(channelinfo)

    def get_code(self, authorize_url):
        """Show authorization URL and return the code the user wrote."""
        import sys
        message = "Check this link in your browser: {0}".format(authorize_url)
        sys.stderr.write(message + "\n")
        return input("Enter verification code: ")

    def test_get_channel_credential(self):
        handler = YoutubeChannelHandler('Movie Recap')
        handler.get_youtube_handler(handler.auth_confirm)
        info = handler.get_channel_name()
        print(info)

    def test_list_all_channel(self):
        infos = YtChannelDb().list_all_page_info()
        for each_info in infos:
            each_info: ChannelInfo
            print(each_info.toJSON())

    def test_add_channel(self):
        handler = YoutubeChannelHandler()
        handler.add_new_channel()
        info = handler.get_channel_name()
        print(info)
