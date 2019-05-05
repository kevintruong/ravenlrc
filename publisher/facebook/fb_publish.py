#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import os
import subprocess

import requests
from facepy import GraphAPI

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, 'db')
GetTokenScript = os.path.join(CurDir, 'gettoken.php')
fbpageinfo = os.path.join(AuthenticateFileDir, 'pages.json')


def php(script_path, username, password):
    p = subprocess.Popen(['php', '-f', script_path, username, password], stdout=subprocess.PIPE)
    result = p.communicate()[0]
    return result


class PageInfo:
    def __init__(self, id, name, token):
        self.id = id
        self.name = name
        self.token = token


class AccInfo:
    def __init__(self, username, password, token=None):
        if not os.path.exists(fbpageinfo):
            self.username = username
            self.password = password
            if token:
                self.token = token
            else:
                self.token = self.gettoken()
            self.pages = []
            self.collect_pagesinfo()
            self.toJSON()

    def gettoken(self):
        get_token = php(GetTokenScript, "{}".format(self.username),
                        "{}".format(self.password)).decode('utf-8')
        userinfo = json.loads(get_token)
        token = userinfo['access_token']
        return token

    def get_account_info(self):
        payload = {'method': 'get', 'access_token': self.token}
        fbrsp = requests.get('https://graph.facebook.com/v2.8/me/accounts?limit=1000', payload).json()
        return fbrsp['data']

    def collect_pagesinfo(self):
        account_info = self.get_account_info()
        for each_page in account_info:
            self.pages.append(PageInfo(each_page['id'], each_page['name'], each_page['access_token']))

    def toJSON(self):
        with open(fbpageinfo, 'w') as fbdb:
            return json.dump(self, fbdb, default=lambda o: o.__dict__,
                             sort_keys=True, indent=2)


class FbPageAPI:
    fbpage_file = os.path.join(AuthenticateFileDir, 'fbpage.json')

    def __init__(self, page_name=None):
        if os.path.exists(fbpageinfo):
            self.authenticate_page(page_name)
        else:
            raise FileNotFoundError

    def authenticate_page(self, page_name):
        with open(fbpageinfo, 'r') as fbpage:
            page_autth = json.load(fbpage)
            for each_page in page_autth['pages']:
                if page_name.lower() in each_page['name'].lower():
                    self.page_access_token = each_page['token']
                    self.pageid = each_page['id']
            self.graph = GraphAPI(self.page_access_token)

    #
    # def __init__(self, page_name=None):
    #     with open(self.fbpage_file, 'r') as fbpage:
    #         accountdata = json.load(fbpage)
    #     for account in accountdata['account']:
    #         accinfo = AccInfo(account['username'], account['password'])

    def _get_accounts(self, limit=250):
        self.accounts = self.graph.get('me/accounts?limit=' + str(limit))
        return self.accounts['data']

    def get_accounts(self):
        return self.accounts['data']

    def get_page_access_token(self, _page_id):
        """
            :param _page_id:
            :return: page_specific_token
        """
        for data in self.accounts:
            if _page_id == data['id']:
                _page_access_token = data['access_token']
                print('')
                print('Page id: ', data['id'])
                print('Page Name: ', data['name'])
                return _page_access_token
        else:
            return None

    def post(self, image_file=None, message=None, link=None, video_file=None):
        """
             Method to post the media and text message to your page you manage.
             :param page_access_token: valid api token
             :param image_file: Image File along with path
             :param message: Text
             :return: None
         """
        import time
        next_threedays = 3 * 3600 * 24
        curtimestamp = int(time.time()) + next_threedays
        try:
            print('Posting .....')
            if image_file:
                image_file = open(image_file, 'rb')
                if message:
                    self.graph.post(path=self.pageid + '/photos',
                                    source=image_file,
                                    message=message)
                else:
                    self.graph.post(path=self.pageid + '/photos',
                                    source=image_file)
            elif video_file:
                if message:
                    self.graph.post(path=self.pageid + '/videos',
                                    description=message,
                                    published=False,
                                    scheduled_publish_time=curtimestamp,
                                    source=video_file)
                else:
                    self.graph.post(path=self.pageid + '/videos',
                                    source=video_file,
                                    published=False,
                                    scheduled_publish_time=curtimestamp)
            else:
                if not message:
                    message = 'Hello everyone!!'
                self.graph.post(path=self.pageid + '/feed',
                                message=message,
                                link=link,
                                published=False,
                                scheduled_publish_time=curtimestamp)
            print('Posted Successfully !! ..')
        except Exception as error:
            print('Posting failed .. ', str(error))

    def post_yt_mv_des(self, mvsnippet: dict, mvid: str):
        try:
            description = mvsnippet['description']
            link = "https://www.youtube.com/watch?v={}".format(mvid)
            post = description
            self.post(message=post, link=link)
            pass
        except Exception as exp:
            from backend.yclogger import telelog
            telelog.error('can not post mvid {}'.format(exp))

    def post_video(self, mvsnippet: dict, id, videofile):
        try:
            ytlink = 'https://youtu.be/{}'.format(id)
            description = mvsnippet['description']
            post = description + '\n' + ytlink
            with open(videofile, 'rb') as videofd:
                self.post(message=post, video_file=videofd)
            pass
        except Exception as exp:
            from backend.yclogger import telelog
            telelog.error('can not post mvid {}'.format(exp))


import unittest


class Test_Facebook_Page_Api(unittest.TestCase):
    def setUp(self) -> None:
        self.acc = AccInfo(r'vu_spk08117@yahoo.com', r'maidongvu')

    def test_page_post(self):
        try:
            fbpage = FbPageAPI('timshel')
            fbpage.post(message='hello world , #timshel')
        except Exception as exp:
            from backend.yclogger import stacklogger
            from backend.yclogger import slacklog
            slacklog.error(stacklogger.format(exp))

    def test_youtube_post(self):
        from publisher.youtube.youtube_uploader import YtMvConfigStatus
        from publisher.youtube.YoutubeMVInfo import YtMvConfigSnippet
        from publisher.youtube.YoutubeMVInfo import YoutubeMVInfo
        from backend.type import SongInfo
        from crawler.cmder import CrawlCmder
        url = 'https://www.nhaccuatui.com/bai-hat/khong-la-cua-nhau-sidie-ft-nho.P6NrlAGU7HSs.html'

        crawlerdict = {'url': url}
        crawler = CrawlCmder(crawlerdict)
        self.song: SongInfo = SongInfo(json.loads(crawler.run()))

        status = YtMvConfigStatus(3)
        snippet = YtMvConfigSnippet.create_snippet_from_info(YoutubeMVInfo('timshel',
                                                                           self.song))

        try:
            fbpage = FbPageAPI('timshel')
            fbpage.post_video(mvsnippet=snippet.to_dict(),
                              id='YzrSI1LlAv4',
                              videofile='/mnt/Data/Project/ytcreatorservice/test/sample_data/sub_output.mp4')
        except Exception as exp:
            from backend.yclogger import stacklogger
            from backend.yclogger import slacklog
            slacklog.error(stacklogger.format(exp))


class Test_Account_Info(unittest.TestCase):

    def setUp(self) -> None:
        self.acc = AccInfo(r'vu_spk08117@yahoo.com', r'Thuyanh3003')

    def test_get_account_info(self):
        accinfo = self.acc.get_account_info()
        print(accinfo)

    def test_collect_page_info(self):
        self.acc.collect_pagesinfo()
        print(self.acc.toJSON())
