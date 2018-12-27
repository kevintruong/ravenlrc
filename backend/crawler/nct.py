import requests

import abc
import json


class crawler(abc.ABC):

    @abc.abstractmethod
    def getdownload(self):
        pass


class nctcrawler(crawler):

    def getdownload(self):
        pass

    nctWmUrl = "https://m.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://m.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3="
    songkey = r'songencryptkey=\"([a-zA-Z0-9]*)\"'

    def __init__(self, ncturl: str):
        songinfos = ncturl.split("/")
        songid = songinfos[4]
        self.mobileNctWmUrl = nctcrawler.nctWmUrl + '{}'.format(songid)
        pass

    def get_songkey(self, htmlbody):
        import re
        express = re.compile(nctcrawler.songkey)
        matchlist = express.findall(htmlbody)
        if len(matchlist):
            return matchlist[0]
        raise Exception("not found song key encrypt")

    def parser(self):
        body = requests.get(self.mobileNctWmUrl)
        html = body._content.decode('utf-8')
        songkey = self.get_songkey(html)
        downloadlink = nctcrawler.nctLinkInfo.format(songkey)
        print(downloadlink)
        body = requests.get(downloadlink)
        resjson = json.loads(body._content.decode('utf-8'))['data']['location']
        print(resjson)
        return resjson

        pass


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html'

    def test_init(self):
        nct = nctcrawler(self.url)
        self.assertEqual(nct.mobileNctWmUrl, nctcrawler.nctWmUrl + "dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html")

    def test_parse(self):
        nct = nctcrawler(self.url)
        self.assertEqual(nct.mobileNctWmUrl, nctcrawler.nctWmUrl + "dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html")
        nct.parser()
