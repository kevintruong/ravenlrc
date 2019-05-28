#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import json
import os

from facepy import GraphAPI

from publisher.facebook.account import AccInfo, FbPageInfoDb

CurDir = os.path.dirname(os.path.realpath(__file__))
AuthenticateFileDir = os.path.join(CurDir, 'db')

fbpageinfo = os.path.join(AuthenticateFileDir, 'pages.json')


class FbPageAPI:
    fbpage_file = os.path.join(AuthenticateFileDir, 'fbpage.json')

    def __init__(self, page_name=None):
        pageinfo = FbPageInfoDb().get_page_info_by_name(page_name)
        if pageinfo:
            self.graph = GraphAPI(pageinfo.token)
            self.pageid = pageinfo.id
        else:
            raise Exception('not found page info in DB')

    def post_video(self, video_file,
                   description,
                   publish_time=None, title=None):
        try:
            if publish_time is None:
                import time
                next_threedays = 3 * 3600 * 24
                publish_time = int(time.time()) + next_threedays
            if title is None:
                from backend.utility.Utility import FileInfo
                fileinfo = FileInfo(video_file)
                title = fileinfo.name
            postvid_req = {'source': video_file}
            postvid_req.update({'description': description})
            postvid_req.update({'scheduled_publish_time': publish_time})
            postvid_req.update({'published': False})
            postvid_req.update({'title': title})
            self.graph.post(path=self.pageid + '/videos', retry=2, **postvid_req)
        except Exception as exp:
            from backend.yclogger import stacklogger, slacklog, telelog
            msg = stacklogger.format(exp)
            slacklog.error(msg)

    def post(self,
             image_file=None,
             message=None,
             link=None,
             video_file=None):
        """
             Method to post the media and text message to your page you manage.
             :param video_file:
             :param link:
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

    # def post_video(self, mvsnippet: dict, id, videofile):
    #     try:
    #         ytlink = 'https://youtu.be/{}'.format(id)
    #         description = mvsnippet['description']
    #         post = description + '\n' + ytlink
    #         with open(videofile, 'rb') as videofd:
    #             self.post(message=post, video_file=videofd)
    #         pass
    #     except Exception as exp:
    #         from backend.yclogger import telelog
    #         telelog.error('can not post mvid {}'.format(exp))


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
        from publisher.youtube.uploader import YtMvConfigStatus
        from publisher.youtube.info import YtMvConfigSnippet
        from publisher.youtube.info import YoutubeMVInfo
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
        self.page = FbPageAPI('Subtitle Recap Movie')

    def test_collect_page_info(self):
        self.page.post(message='hello world')
