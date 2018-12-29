import codecs
import os

import requests

import abc
import json

from backend.crawler.rc4_py3 import decrypt
from backend.utility.TempFileMnger import *


class Crawler(abc.ABC):

    @abc.abstractmethod
    def getdownload(self, outputdir: str):
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


class NctCrawler(Crawler):
    nctWmUrl = "https://m.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://m.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3="
    songkey = r'songencryptkey=\"([a-zA-Z0-9]*)\"'
    key = "Lyr1cjust4nct"

    def __init__(self, ncturl: str):
        songinfos = ncturl.split("/")
        songid = songinfos[4]
        self.mobileNctWmUrl = NctCrawler.nctWmUrl + '{}'.format(songid)
        pass

    def get_songkey(self, htmlbody):
        import re
        express = re.compile(NctCrawler.songkey)
        matchlist = express.findall(htmlbody)
        if len(matchlist):
            return matchlist[0]
        raise Exception("not found song key encrypt")

    def parser(self):
        body = requests.get(self.mobileNctWmUrl)
        html = body._content.decode('utf-8')
        songkey = self.get_songkey(html)
        downloadlink = NctCrawler.nctLinkInfo.format(songkey)
        print(downloadlink)
        body = requests.get(downloadlink)
        songinfodata = json.loads(body._content)
        songinf = SongInfo(songinfodata['data'])
        return songinf

    def getdownload(self, outputdir: str):
        songinfo: SongInfo = self.parser()
        mp3file = requests.get(songinfo.localtion, allow_redirects=True)
        localmp3file = os.path.join(outputdir, '{}_{}.mp3'.format(songinfo.title, songinfo.singerTitle))
        locallyricfile = os.path.join(outputdir, '{}.lrc'.format(songinfo.title))
        with open(localmp3file, 'wb') as mp3filefd:
            mp3filefd.write(mp3file.content)
            mp3filefd.close()
        lyricfile = requests.get(songinfo.lyric, allow_redirects=True)
        returndata = decrypt(NctCrawler.key, lyricfile.content)
        with codecs.open(locallyricfile, 'w', "utf-8") as f:
            f.write(returndata)
        # open(locallyricfile, 'w').write(returndata)
        songinfo.localtion = localmp3file
        songinfo.lyric = locallyricfile
        return songinfo.toJSON()


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html'
        self.nct = NctCrawler(self.url)

    def test_init(self):
        self.assertEqual(self.nct.mobileNctWmUrl, NctCrawler.nctWmUrl + "dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html")

    def test_parse(self):
        self.assertEqual(self.nct.mobileNctWmUrl, NctCrawler.nctWmUrl + "dai-lo-tan-vo-uyen-linh.QDJIU9iDNHfI.html")
        nctinfo = self.nct.parser()
        print(nctinfo)
        jsondat = json.loads(nctinfo)
        print('end')

    def test_download_file(self):
        self.nct.getdownload('./test/')
