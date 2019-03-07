import datetime
import http.client
import http.client as httplib
import json
import os
import random
import time

import httplib2
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from backend.utility.Utility import todict
from backend.publisher.youtube import auth
from enum import Enum

from backend.publisher.youtube.YoutubeMVInfo import YtMvConfigSnippet, YoutubeMVInfo

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
                        http.client.IncompleteRead, http.client.ImproperConnectionState,
                        http.client.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)
MAX_RETRIES = 1

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, '../Authenticate')

AuthenticateDictFile = {
    "Timshel": os.path.join(AuthenticateFileDir, 'Timshel_credential.json'),
    "ReChannel": os.path.join(AuthenticateFileDir, 'ReChannel_credential.json'),
}


class PrivacyStatus(Enum):
    PRIVACY_STATUS_PRIVATE = 'private'
    PRIVACY_STATUS_PUBLIC = 'public'
    PRIVACY_STATUS_UNLISTED = 'unlisted'


class StatusLicense(Enum):
    STATUS_LICENSE_YOUTUBE = 'youtube'
    STATUS_LICCENSE_COMMON = 'creativeCommon'


class YtMvConfigStatus:
    def __init__(self, delaydays=None):
        """
        return Status metadata for setting the MV will publish in next publishtime from now
        :param delaydays:  next x days from now
        """
        if delaydays is not None:
            publishtime = datetime.datetime.now() + datetime.timedelta(days=delaydays)
            publish_at = publishtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            self.privacyStatus = PrivacyStatus.PRIVACY_STATUS_PRIVATE.value
            self.publishAt = publish_at
        else:
            self.privacyStatus = PrivacyStatus.PRIVACY_STATUS_PRIVATE.value

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
    def __init__(self, channel: str, callback=None):
        self.youtube: Resource = self.get_youtube_handler(channel.lower(), callback)

    @staticmethod
    def get_and_create_credential_file(channelname):
        if channelname in AuthenticateDictFile:
            return AuthenticateDictFile[channelname]
        else:
            return None

    @staticmethod
    def get_secret_file():
        return os.path.join(AuthenticateFileDir, 'client_secrets.json')

    def get_youtube_handler(self, channelname, callback=None):
        """Return the API Youtube object."""
        try:

            default_credentials = self.get_and_create_credential_file(channelname)
            if default_credentials is None:
                default_credentials = os.path.join(AuthenticateFileDir, '{}_credential.json'.format(channelname))
            client_secrets = self.get_secret_file()

            credentials = default_credentials
            if callback is None:
                get_code_callback = backend.publisher.youtube.auth.console.get_code
            else:
                get_code_callback = callback
            return auth.get_resource(client_secrets, credentials,
                                     get_code_callback=get_code_callback)
        except Exception as exp:
            print(exp)
            raise exp

    def upload_video(self, fileupload: os.path,
                     snippet: YtMvConfigSnippet = None,
                     status: YtMvConfigStatus = None):
        def resumable_upload(request):
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
                        return response
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

        youtube = self.youtube
        body = dict(
            snippet=snippet.to_dict(),
            status=status.to_dict(),
        )

        print(json.dumps(body, indent=True))

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(fileupload, chunksize=-1, resumable=True)
        )
        respond = resumable_upload(insert_request)
        return respond

    def get_video_info_by_id(self, id: str):
        video_rsp = self.youtube.videos().list(part='snippet,status', id=id).execute()
        if len(video_rsp['items']):
            info = video_rsp['items'][0]
            return info
        else:
            return None

    def update_video_by_id(self, mvid, snippet: YtMvConfigSnippet, status: YtMvConfigStatus):
        youtube = self.youtube
        body = {}
        if snippet:
            body['snippet'] = snippet.to_dict()
        if status:
            body['status'] = status.to_dict()
        body['id'] = mvid
        print(json.dumps(body, indent=True))
        updatersp = youtube.videos().update(part=','.join(body.keys()), body=body).execute()
        return updatersp

    def remove_video_by_id(self, videoid: str):
        try:
            self.youtube.videos().delete(id=videoid,
                                         onBehalfOfContentOwner=None).execute()
        except Exception as exp:
            print(exp)
            raise exp


import unittest


class TestMvconfig(unittest.TestCase):
    def setUp(self):
        self.YtMvInfo = YoutubeMVInfo('timshel', 'em à')
        tags = self.YtMvInfo.hashtags
        self.snippet = YtMvConfigSnippet(self.YtMvInfo.title, self.YtMvInfo.description, tags)

    def test_snippet_to_dict(self):
        print(self.snippet.to_dict())

    def test_status_to_dict(self):
        status = YtMvConfigStatus(5)
        print(status.to_dict())
