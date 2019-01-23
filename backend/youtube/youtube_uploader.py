import datetime
import json
import random
import sys
import os
import time

import httplib2
import http.client
import http.client as httplib

from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage
from oauth2client import file as oauth_file, client, tools
import backend.youtube.auth
from backend.youtube import auth

cur_dir = os.path.dirname(__file__)
authenticatedir = os.path.join(cur_dir, '../Authenticate')

CREDENTIAL_FILE = os.path.join(authenticatedir, "timshel_credentials.json")
CLIENT_SECRETS_FILE = os.path.join(authenticatedir, 'client_secrets.json')
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

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, '..\Authenticate')

AuthenticateDictFile = {
    "Timshel": os.path.join(AuthenticateFileDir, 'Timshel_credential.json'),
    "ReChannel": os.path.join(AuthenticateFileDir, 'ReChannel_credential.json'),
}


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


from enum import Enum


class PrivacyStatus(Enum):
    PRIVACY_STATUS_PRIVATE = 'private'
    PRIVACY_STATUS_PUBLIC = 'public'
    PRIVACY_STATUS_UNLISTED = 'unlisted'


class StatusLicense(Enum):
    STATUS_LICENSE_YOUTUBE = 'youtube'
    STATUS_LICCENSE_COMMON = 'creativeCommon'


class YtMvConfigSnippet:
    @classmethod
    def tags_formatter(cls, tags: str):
        tags_nospaces = "".join(tags.split())
        tags_list = tags_nospaces.split(',')
        return tags_list

    @classmethod
    def verify_categoryid(cls, id):
        cats = ['', 'Film & Animation', 'Autos & Vehicles', '', '', '', '', '', '', '', 'Music', '', '', '', '',
                'Pets & Animals', '', 'Sports', 'Short Movies', 'Travel & Events', 'Gaming', 'Videoblogging',
                'People & Blogs', 'Comedy', 'Entertainment', 'News & Politics', 'Howto & Style', 'Education',
                'Science & Technology', 'Nonprofits & Activism', 'Movies', 'Anime/Animation', 'Action/Adventure',
                'Classics', 'Comedy', 'Documentary', 'Drama', 'Family', 'Foreign', 'Horror', 'Sci-Fi/Fantasy',
                'Thriller', 'Shorts', 'Shows', 'Trailers']
        this_categoryid = cats[id]
        if len(this_categoryid) == 0:
            return 10  # entertainment categoryId
        return id

    def __init__(self,
                 title,
                 description,
                 categoryId,
                 tags: str):
        # self.channelId = channelid
        self.title = title
        self.description = description
        self.categoryId = self.verify_categoryid(categoryId)
        self.tags = self.tags_formatter(tags)

    def to_dict(self):
        return todict(self)

    pass


class YtMvConfigStatus:
    def __init__(self, privacyStatus=PrivacyStatus.PRIVACY_STATUS_PRIVATE.value, publishAt=None):
        if publishAt:
            self.privacyStatus = PrivacyStatus.PRIVACY_STATUS_PRIVATE.value
            self.publishAt = publishAt
        else:
            self.privacyStatus = privacyStatus

    def to_dict(self):
        return todict(self)

    pass


class YtMvConfigRecordingDetails:
    def __init__(self, recordingdate):
        # self.location = location
        self.recordingDate = recordingdate

    pass


class YoutubeUploader:

    # Authorize the request and store authorization credentials
    def __init__(self, title: str,
                 description: str,
                 tags: list,
                 categoryId: str):
        self.title = title
        self.description = description
        self.tags = tags
        self.categoryID = categoryId
        self.privacyStatus = 'unlisted'
        self.store = Storage(CREDENTIAL_FILE)
        self.youtube: Resource = self.get_youtube_handler('timeshel')

    @staticmethod
    def get_and_create_credential_file(channelname):
        if channelname in AuthenticateDictFile:
            return AuthenticateDictFile[channelname]
        else:
            return None

    def get_secret_file(self):
        return os.path.join(AuthenticateFileDir, 'client_secrets.json')

    def get_youtube_handler(self, channelname):
        """Return the API Youtube object."""
        try:

            default_credentials = self.get_and_create_credential_file(channelname)
            if default_credentials is None:
                default_credentials = os.path.join(AuthenticateFileDir, '{}_credential.json'.format(channelname))
            client_secrets = self.get_secret_file()

            credentials = default_credentials
            get_code_callback = auth.console.get_code
            return auth.get_resource(client_secrets, credentials,
                                     get_code_callback=get_code_callback)
        except Exception as exp:
            print(exp)
            raise exp

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

    def upload_video(self, fileupload: os.path, snippet: YtMvConfigSnippet = None, status: YtMvConfigStatus = None):
        youtube = self.youtube
        if snippet:
            body = dict(
                snippet=snippet.to_dict(),
                status=status.to_dict(),
            )
            pass
        else:
            body = dict(
                snippet=dict(
                    title=self.title,
                    description=self.description,
                    tags=self.tags,
                    categoryId=self.categoryID
                ),
                status=dict(
                    privacyStatus=self.privacyStatus
                ),
            )
        print(json.dumps(body, indent=True))

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(fileupload, chunksize=-1, resumable=True)
        )
        videoId = self.resumable_upload(insert_request)
        return videoId

    def get_video_info_by_id(self, id: str):
        video_rsp = self.youtube.videos().list(part='snippet,status', id=id).execute()
        if len(video_rsp['items']):
            info = video_rsp['items'][0]
            return info
        else:
            return None

    def update_video_by_id(self, id, snippet: dict, status: dict):
        youtube = self.youtube
        body = dict(
            snippet=snippet,
            status=status,
            id=id
        )
        print(json.dumps(body, indent=True))

        # Call the API's videos.insert method to create and upload the video.
        updatersp = youtube.videos().update(part=','.join(body.keys()), body=body).execute()
        return updatersp

    def remove_video_by_id(self, videoid: str):
        try:
            self.youtube.videos().delete(id=videoid, onBehalfOfContentOwner=None).execute()
        except Exception as exp:
            print(exp)
            raise exp

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


import unittest


class TestMvconfig(unittest.TestCase):
    def setUp(self):
        self.snippet = YtMvConfigSnippet("hello, this is my test",
                                         "this is the description",
                                         10,
                                         'this,is,my,tags',
                                         'vn', 'vn')

    def test_snippet_to_dict(self):
        print(self.snippet.to_dict())

    def test_status_to_dict(self):
        publishtime = datetime.datetime.now() + datetime.timedelta(days=3)
        publish_at = publishtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5] + 'Z'
        status = YtMvConfigStatus(publishAt=publish_at)
        print(status.to_dict())
