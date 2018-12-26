import random
import sys
import os
import time

import httplib2
import http.client
import http.client as httplib

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client import file as oauth_file, client, tools

cur_dir = os.path.dirname(__file__)

CREDENTIAL_FILE = os.path.join(cur_dir, "timshel.cre")
CLIENT_SECRETS_FILE = os.path.join(cur_dir, 'client_id.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)
MAX_RETRIES = 10


# TODO
# feature need:
#   - handle End User account (multiple account)
#
class YoutubeUploader:

    # Authorize the request and store authorization credentials
    def __init__(self, title: str, description: str, tags: list, categoryId: str):
        self.title = title
        self.description = description
        self.tags = tags
        self.categoryID = categoryId
        self.privacyStatus = 'unlisted'
        self.store = Storage(CREDENTIAL_FILE)
        self.youtube: Resource = self.get_authenticated_service()

    def set_title(self, title: str):
        self.title = title

    def get_title(self):
        return self.title

    def set_description(self, description: str):
        self.description = description

    def get_description(self):
        return self.description

    def set_tags(self, tags: str):
        self.tags = tags

    def get_tags(self):
        return self.tags

    def set_categoryid(self, categoryid: str):
        self.categoryID = categoryid

    def get_categoryid(self):
        return self.categoryID

    def save_credential_file(self, credential_file):
        self.store.put(credential_file)

    def get_credential_file(self):
        return self.store.get()

    def get_authenticated_service(self):
        if not os.path.isfile(CLIENT_SECRETS_FILE):
            print("Not found {}".format(CLIENT_SECRETS_FILE))
        credentials: Credentials = self.store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
            credentials = tools.run_flow(flow, self.store)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    def upload_video(self, fileupload: os.path):
        youtube = self.youtube
        body = dict(
            snippet=dict(
                title=self.title,
                description=self.description,
                tags=self.tags,
                categoryId=self.categoryID
            ),
            status=dict(
                privacyStatus=self.privacyStatus
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(fileupload, chunksize=-1, resumable=True)
        )
        videoId = self.resumable_upload(insert_request)
        return videoId

    def get_video_info_by_id(self, id: str):
        video_rsp = self.youtube.videos().list(part='snippet', id=id).execute()
        info = video_rsp['items'][0]['snippet']
        return info

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def resumable_upload(self, request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                status, response = request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print('Video id "{}" was successfully uploaded.'.format(response['id']))
                    else:
                        exit('The upload failed with an unexpected response: %s' % response)
                    return response['id']
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = 'A retriable HTTP error {:d} occurred:\n{}'.format(e.resp.status,
                                                                               e.content)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = 'A retriable error occurred: %s' % e
            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit('No longer attempting to retry.')
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print('Sleeping {:f} seconds and then retrying...'.format(sleep_seconds))
                time.sleep(sleep_seconds)
