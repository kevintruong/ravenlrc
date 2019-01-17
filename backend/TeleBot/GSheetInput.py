import logging
import os

import gspread as gspread
from google.oauth2.credentials import Credentials
from oauth2client import client, tools
from oauth2client.file import Storage

from backend.crawler.nct import SongInfo

cur_dir = os.path.dirname(__file__)

CREDENTIAL_FILE = os.path.join(cur_dir, "credentials.json")
CLIENT_SECRETS_FILE = os.path.join(cur_dir, 'client_secrets.json')
SCOPES = ['https://spreadsheets.google.com/feeds',
          'https://www.googleapis.com/auth/drive']


class GoogleSheetStream:
    """
    format of element song list
    id,song_name, singer,link,status
    """

    def __init__(self):
        self.store = Storage(CREDENTIAL_FILE)
        self.reset_authenticate()
        self.worksheet = self.get_worksheet()

    def reset_authenticate(self):
        self.gosheet = self.get_authenticated_service()

    def get_authenticated_service(self):
        if not os.path.isfile(CLIENT_SECRETS_FILE):
            print("Not found {}".format(CLIENT_SECRETS_FILE))
        credentials: Credentials = self.store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
            credentials = tools.run_flow(flow, self.store)
        return gspread.authorize(credentials)

    def format_songinfo(self, songinfo: SongInfo):
        return [songinfo.id, songinfo.title, songinfo.singerTitle, songinfo.info]

    def get_worksheet(self, channel_name='timshel'):
        try:
            wks = self.gosheet.open('song list')
        except Exception as e:
            wks = self.gosheet.create('song list')
        try:
            worksheet = wks.worksheet(channel_name)
        except Exception as e:
            # if worksheet is None:
            wks.add_worksheet(channel_name, rows=1000, cols=30)
            worksheet = wks.worksheet(channel_name)
        return worksheet

    def emit(self, songinfo: SongInfo, worksheet='timshel'):
        worksheet_name = str(worksheet)
        fail_count = 0
        while True:
            try:
                self.worksheet = self.get_worksheet(worksheet_name)
                row = self.is_url_existed(songinfo.id)
                if row is not True:
                    self.worksheet.append_row(self.format_songinfo(songinfo))
                    return True
                return False
            except Exception as exp:
                fail_count = fail_count + 1
                self.reset_authenticate()
                if fail_count > 3:
                    raise exp

    def is_url_existed(self, url):
        devid_cells = self.worksheet.findall(url)
        if len(devid_cells):
            return True
        return False
