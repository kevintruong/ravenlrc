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
        self.info = nctsonginfo['info']
        self.title = nctsonginfo['title']
        self.lyric = nctsonginfo['lyric']
        self.location = nctsonginfo['location']


class NctCrawler(Crawler):
    nctWmUrl = "https://m.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://m.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3="
    songkey = r'songencryptkey=\"([a-zA-Z0-9]*)\"'
    key = "Lyr1cjust4nct"

    def __init__(self, ncturl: str):
        songinfos = ncturl.split("/")
        songid = songinfos[4]
        self.mobileNctWmUrl = NctCrawler.nctWmUrl + '{}'.format(songid)
        self.songinfo = self.parser()
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

    def get_songinfo(self):
        return self.songinfo.toJSON()

    def getdownload(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        localmp3file = self.get_mp3file(outputdir)
        locallyricfile = self.get_lyric(outputdir)
        songinfo.location = localmp3file
        songinfo.lyric = locallyricfile
        return songinfo.toJSON()

    def get_mp3file(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        mp3file = requests.get(songinfo.location, allow_redirects=True)
        localmp3file = os.path.join(outputdir, '{}_{}.mp3'.format(songinfo.title, songinfo.singerTitle)).encode('utf-8')
        with open(localmp3file, 'wb') as mp3filefd:
            mp3filefd.write(mp3file.content)
            mp3filefd.close()
        return localmp3file.decode('utf8')

    def get_lyric(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        locallyricfile = os.path.join(outputdir, '{}.lrc'.format(songinfo.title)).encode('utf-8')
        lyricfile = requests.get(songinfo.lyric, allow_redirects=True)
        returndata = decrypt(NctCrawler.key, lyricfile.content)
        with codecs.open(locallyricfile, 'w', "utf-8") as f:
            f.write(returndata)
        return locallyricfile.decode('utf-8')


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html'
        self.nct = NctCrawler(self.url)

    def test_init(self):
        self.assertEqual(self.nct.mobileNctWmUrl,
                         NctCrawler.nctWmUrl + "nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")

    def test_parse(self):
        self.assertEqual(self.nct.mobileNctWmUrl,
                         NctCrawler.nctWmUrl + "nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")
        print(self.nct.get_songinfo())
        print('end')

    def test_download_file(self):
        jsondat = self.nct.getdownload('./test/')
        print(jsondat)

    def test_get_lyric(self):
        jsonfile = self.nct.get_lyric('./test/')
        print(jsonfile)

    def test_get_mp3file(self):
        jsonfile = self.nct.get_mp3file()
        print(jsonfile)
