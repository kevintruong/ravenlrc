import os
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from backend.utility.Utility import FileInfo

CurDir = os.path.dirname(os.path.realpath(__file__))
ClientSecretfile = os.path.join(CurDir, 'client_secrets.json')

SCOPES = 'https://www.googleapis.com/auth/drive'


class GDriveMnger:

    def __init__(self):
        self.login()
        pass

    def login(self):
        token = os.path.join(CurDir, 'auth.json')
        store = file.Storage(token)
        self.creds = store.get()
        if not self.creds or self.creds.invalid:
            client_id = ClientSecretfile
            flow = client.flow_from_clientsecrets(client_id, SCOPES)
            flags = tools.argparser.parse_args(args=[])
            flags.noauth_local_webserver = True
            self.creds = tools.run_flow(flow, store, flags)

    def list_file(self):
        return

    def get_share_link(self, filepath: str):
        filename = FileInfo(filepath)
        fileinfo = self.viewFile(filename)
        if 'webContentLink' in fileinfo:
            return fileinfo['webContentLink']
        return None

    def generate_html_preview_file(self, filepath: str):
        from backend.utility.Utility import FileInfo
        fileinfo = FileInfo(filepath)
        timeout = 0
        import time
        while True:
            previewlink = self.get_share_link(fileinfo.filename)
            if previewlink:
                break
            time.sleep(3)
            timeout = timeout + 1
            if timeout > 3:
                return None
        print(previewlink)
        preview_html = """<html>
                <head>
                    <title>Video Test</title>
                </head>
                <body>
                    <video controls="controls">
                        <source src="{}" type='video/mp4'/>
                    </video>
                </body>
                </html>
                """.format(previewlink)
        from backend.utility.TempFileMnger import HtmlTempFile
        htmlfile = HtmlTempFile(pre='preview').getfullpath()
        with open(htmlfile, 'w') as previewfile:
            previewfile.write(preview_html)
        return htmlfile

    def viewFile(self, name=None):

        """
        view-files: Filter based list of the names and ids of the first 10 files the user has access to
        """
        creds = self.creds
        service = build('drive', 'v3', http=creds.authorize(Http()))
        page_token = None
        query = "name contains '" + name + "' "
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name,webContentLink)',
                                        pageToken=page_token).execute()
        templist = [response.get('files', [])[i:i + 25] for i in
                    range(0, len(response.get('files', [])), 25)]  # breakdown list to 25 entries at a time
        if len(templist):
            if len(templist[0]):
                return templist[0][0]
        else:
            return None


def generate_html_file(output: str):
    gdriver = GDriveMnger()
    previewfile = gdriver.generate_html_preview_file(output)
    return previewfile


import unittest


class Test_GoogleFiles(unittest.TestCase):
    def setUp(self):
        self.gdriver = GDriveMnger()

    def test_get_share_link(self):
        self.gdriver.login()
        files = self.gdriver.viewFile('nham_mat_thay_mua_he.mp4')
        print(files)
        # sharelink = self.gdriver.get_share_link('nham_mat_thay_mua_he.mp4')
        # print(sharelink)
