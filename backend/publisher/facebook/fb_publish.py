#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import os
import subprocess

import requests
from facepy import GraphAPI

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, '../../auth')
GetTokenScript = os.path.join(CurDir, 'gettoken.php')
FacebookDb = os.path.join(CurDir, 'pages.json')


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
        self.username = username
        self.password = password
        if token:
            self.token = token
        else:
            self.token = self.gettoken()
        self.pages = []

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
        with open(FacebookDb, 'w') as fbdb:
            return json.dump(self, fbdb, default=lambda o: o.__dict__,
                             sort_keys=True, indent=2)


class FbPageAPI:
    fbpage_file = os.path.join(AuthenticateFileDir, 'fbpage.json')

    def __init__(self, page_name=None):
        with open(self.fbpage_file, 'r') as fbpage:
            accountdata = json.load(fbpage)
        for account in accountdata['account']:
            accinfo = AccInfo(account['username'], account['password'])

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
                # print('access_token: ', _page_access_token)
                print('')
                print('Page id: ', data['id'])
                print('Page Name: ', data['name'])
                return _page_access_token
        else:
            return None

    def post(self, image_file=None, message=None, link=None):
        """
             Method to post the media and text message to your page you manage.
             :param page_access_token: valid api token
             :param image_file: Image File along with path
             :param message: Text
             :return: None
         """
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
            else:
                if not message:
                    message = 'Hello everyone!!'
                self.graph.post(path=self.pageid + '/feed', message=message, link=link)
            print('Posted Successfully !! ..')
        except Exception as error:
            print('Posting failed .. ', str(error))

    def post_yt_mv_des(self, mvsnippet: dict, mvid: str):
        tags = ','.join(mvsnippet['tags'])
        description = mvsnippet['description']
        link = "https://www.youtube.com/watch?v={}".format(mvid)
        post = tags + '\n' + description
        self.post(message=post, link=link)
        pass


import unittest


class Test_Facebook_Page_Api(unittest.TestCase):

    def test_page_post(self):
        fbpage = FbPageAPI('timshel')
        # data = fbpage._get_accounts()
        # print(data)
        # fbpage.post(message='hello world , #timshel')


class Test_Account_Info(unittest.TestCase):

    def setUp(self) -> None:
        self.acc = AccInfo(r'vu_spk08117@yahoo.com', r'Thuyanh3003')

    def test_get_account_info(self):
        accinfo = self.acc.get_account_info()
        print(accinfo)

    def test_collect_page_info(self):
        self.acc.collect_pagesinfo()
        print(self.acc.toJSON())
