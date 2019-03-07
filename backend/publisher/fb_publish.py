#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os

from facepy import GraphAPI
import json5

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, '../Authenticate')


class FbPageAPI:
    fbpage_file = os.path.join(AuthenticateFileDir, 'fbpage.json5')

    def __init__(self, page_name=None):
        with open(self.fbpage_file, 'r') as fbpage:
            page_autth = json5.load(fbpage)
        for each_page in page_autth['pageinfo']:
            if page_name in each_page['pagename']:
                self.page_access_token = each_page['token']
                self.pageid = each_page['pageid']
        self.graph = GraphAPI(self.page_access_token)

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
        fbpage.post(message='hello world , #timshel')
