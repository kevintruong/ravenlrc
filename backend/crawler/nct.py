import abc
import codecs
import json
import os

import requests
from bs4 import BeautifulSoup

from backend.crawler.crawler import SeleniumCrawler
from backend.crawler.rc4_py3 import decrypt


# from backend.utility.TempFileMnger import *
# from backend.utility.Utility import FileInfo
from backend.utility.Utility import FileInfo


class Crawler(abc.ABC):

    @abc.abstractmethod
    def getdownload(self, outputdir: str):
        pass

    @abc.abstractmethod
    def get_songinfo(self):
        pass


class SongInfoCrawler:
    @classmethod
    def get_song_info(cls, url):
        if 'nhaccuatui' in url:
            return NctCrawler(url).songinfo
        else:
            raise Exception('not support crawl song info from {}'.format(url))


class SongInfo:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, nctsonginfo=None):
        self.singer = None
        self.info = None
        self.title = None
        self.songfile = None
        self.id = None
        self.lyrictext = None
        self.lyric = None
        self.id = None
        if nctsonginfo:
            for keyvalue in nctsonginfo.keys():
                if keyvalue == 'singer':
                    self.singer = nctsonginfo[keyvalue]
                if keyvalue == 'info':
                    self.info = nctsonginfo[keyvalue]
                if keyvalue == 'title':
                    self.title = nctsonginfo[keyvalue]
                if keyvalue == 'songfile':
                    self.songfile = nctsonginfo[keyvalue]
                    from backend.render.cache import SongFile
                    self.songfile = SongFile.get_fullpath(self.songfile)
                if keyvalue == 'id':
                    self.id = nctsonginfo[keyvalue]
                if keyvalue == 'lyrictext':
                    self.lyrictext = nctsonginfo[keyvalue]
                if keyvalue == 'lyric':
                    from backend.render.cache import SongFile
                    self.lyric = nctsonginfo[keyvalue]
                    self.lyric = SongFile.get_fullpath(self.lyric)

    pass


class NctSongInfo(SongInfo):

    def __init__(self, nctsonginfo: dict):
        super().__init__()
        for keyvalue in nctsonginfo.keys():
            if keyvalue == 'singerTitle':
                self.singer = nctsonginfo[keyvalue]
            if keyvalue == 'info':
                self.info = nctsonginfo[keyvalue]
            if keyvalue == 'title':
                self.title = nctsonginfo[keyvalue]
            if keyvalue == 'location':
                self.songfile = nctsonginfo[keyvalue]
            if keyvalue == 'id':
                self.id = nctsonginfo[keyvalue]
            if keyvalue == 'lyric_text':
                self.lyrictext = nctsonginfo[keyvalue]
            if keyvalue == 'lyric':
                self.lyric = nctsonginfo[keyvalue]
        self.id = self.get_nct_id(self.info)

    def get_nct_id(self, ncturl: str):
        nct_url = ncturl.split('.')
        return nct_url[3]


class NctCrawler(Crawler):
    nctWmUrl = "https://www.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://www.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3=&ip=123.23.58.251"
    songkey = r'songencryptkey=\"([a-zA-Z0-9]*)\"'
    key = "Lyr1cjust4nct"

    def __init__(self, ncturl: str):
        if self.nctWmUrl not in ncturl:
            songinfos = ncturl.split("/")
            songid = songinfos[4]
            self.mobileNctWmUrl = NctCrawler.nctWmUrl + '{}'.format(songid)
        else:
            self.mobileNctWmUrl = ncturl
        self.songinfo: NctSongInfo = self.parser()
        pass

    def get_songkey(self, htmlbody):
        import re
        express = re.compile(NctCrawler.songkey)
        matchlist = express.findall(htmlbody)
        if len(matchlist):
            return matchlist[0]
        raise Exception("{}".format(htmlbody))

    def reformat_lyric(self, lyric_text: str):
        format_lyric = ""
        for line in lyric_text.splitlines():
            format_lyric = format_lyric + " ".join(line.split()) + '\n'
        return format_lyric.replace('  ', '').replace('\n\n', '\n')

        pass

    def get_song_xml_file(self, html_txt: str):
        for line in html_txt.split('\n'):
            if 'player.peConfig.xmlURL' in line:
                return line.split('=', 1)[1].replace('"', '').replace(';', '')

    def song_info_xml_parser(self, xml_text):
        fields = ['title', 'creator', 'location', 'info', 'lyric', 'key']
        doc_el = BeautifulSoup(xml_text, 'xml')
        songinfo = SongInfo()
        for each_fields in fields:
            var = [el.text for el in doc_el.findAll(each_fields)]
            if len(var):
                value: str = var[0].replace('\n', '').replace('  ', '')
                print(value)
                if each_fields == 'title':
                    songinfo.title = value
                if each_fields == 'creator':
                    songinfo.singer = value
                if each_fields == 'location':
                    songinfo.songfile = value
                if each_fields == 'lyric':
                    songinfo.lyric = value
                if each_fields == 'key':
                    songinfo.id = value
                if each_fields == 'info':
                    songinfo.info = value
        return songinfo

    def parser(self):
        crawler = requests.get(self.mobileNctWmUrl)
        song_xml = self.get_song_xml_file(crawler.text)
        song_info = requests.get(song_xml)
        soup = BeautifulSoup(crawler.text, 'html')
        lyric_text = soup.find(attrs={'class': 'lyric'}).text
        formatlyric = self.reformat_lyric(lyric_text)
        songinf = self.song_info_xml_parser(song_info.text)
        songinf.lyrictext = formatlyric
        return songinf

    def get_songinfo(self):
        return self.songinfo.toJSON()

    def getdownload(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        localmp3file = self.get_mp3file(outputdir)
        locallyricfile = self.get_lyric(outputdir)
        songinfo.songfile = FileInfo(localmp3file).filename
        songinfo.lyric = FileInfo(locallyricfile).filename
        return songinfo.toJSON()

    def get_mp3file(self, outputdir: str):
        try:
            songinfo: SongInfo = self.songinfo
            mp3file = requests.get(songinfo.songfile, allow_redirects=True)
            localmp3file = os.path.join(outputdir, '{}_{}.mp3'.format(songinfo.title, songinfo.singer)).encode('utf-8')
            with open(localmp3file, 'wb') as mp3filefd:
                mp3filefd.write(mp3file.content)
                mp3filefd.close()
            return localmp3file.decode('utf8')
        except Exception as exp:
            raise Exception('can not get mp3 file from the url {}'.format(self.songinfo.info))

    def get_lyric(self, outputdir: str):
        try:
            songinfo: SongInfo = self.songinfo
            locallyricfile = os.path.join(outputdir, '{}.lrc'.format(songinfo.title)).encode('utf-8')
            lyricfile = requests.get(songinfo.lyric, allow_redirects=True)
            returndata = decrypt(NctCrawler.key, lyricfile.content)
            with codecs.open(locallyricfile, 'w', "utf-8") as f:
                f.write(returndata)
            return locallyricfile.decode('utf-8')
        except Exception as exp:
            raise Exception('can not get lyric file from the url {}'.format(self.songinfo.info))

    def get_lyric_text(self):
        pass


# class NctCrawler_fix():
#     def __init__(self):


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/giu-cho-em-mot-the-gioi-trang-ft-khoa-vu.yuJlBrY4KIqO.html'
        self.nct = NctCrawler(self.url)

    def test_init(self):
        self.assertEqual(self.nct.mobileNctWmUrl,
                         NctCrawler.nctWmUrl + "nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")

    def test_parse(self):
        # self.assertEqual(self.nct.mobileNctWmUrl,
        #                  NctCrawler.nctWmUrl + "nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")
        print(self.nct.get_songinfo())
        print('end')

    def test_download_file(self):
        jsondat = self.nct.getdownload('./test/')
        print(jsondat)

    def test_get_lyric(self):
        jsonfile = self.nct.get_lyric('./test/')
        print(jsonfile)

    def test_get_mp3file(self):
        jsonfile = self.nct.get_mp3file('./test/')
        print(jsonfile)

    def test_get_song_info(self):
        songinfo = self.nct.songinfo
        info = [songinfo.id, songinfo.title, songinfo.singer, songinfo.info]
        print(info)
