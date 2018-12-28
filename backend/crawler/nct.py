import requests

import abc
import json


class crawler(abc.ABC):

    @abc.abstractmethod
    def getdownload(self):
        pass


class SongInfo:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, nctsonginfo: dict):
        self.singerTitle = nctsonginfo['singerTitle']
        self.songurl = nctsonginfo['info']
        self.title = nctsonginfo['title']
        self.lyric = nctsonginfo['lyric']
        self.localtion = nctsonginfo['location']


def create_songinfo_obj(d):
    return SongInfo(d)


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
        songinfodata = json.loads(body._content)
        songinf = create_songinfo_obj(songinfodata['data'])
        return songinf.toJSON()


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
        nctinfo = nct.parser()
        print(nctinfo.encode('utf-8'))
        jsondat = json.loads(nctinfo)
        print('end')
