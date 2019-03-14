import abc
import codecs
import json

import requests
from bs4 import BeautifulSoup

from backend.crawler.rc4_py3 import decrypt
from backend.utility.TempFileMnger import *


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
                if keyvalue == 'id':
                    self.id = nctsonginfo[keyvalue]
                if keyvalue == 'lyrictext':
                    self.lyrictext = nctsonginfo[keyvalue]
                if keyvalue == 'lyric':
                    self.lyric = nctsonginfo[keyvalue]

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
    nctWmUrl = "https://m.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://m.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3="
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
        raise Exception("not found song key encrypt")

    def reformat_lyric(self, lyric_text: str):
        format_lyric = ""
        for line in lyric_text.splitlines():
            format_lyric = format_lyric + " ".join(line.split()) + '\n'
        return format_lyric

        pass

    def parser(self):
        body = requests.get(self.mobileNctWmUrl)
        soup = BeautifulSoup(body.text, 'html.parser')
        lyric_text = soup.find(attrs={'class': 'lyric'}).text
        formatlyric = self.reformat_lyric(lyric_text)
        # print(formatlyric)
        html = body._content.decode('utf-8')
        songkey = self.get_songkey(html)
        downloadlink = NctCrawler.nctLinkInfo.format(songkey)
        print(downloadlink)

        cookies = r'autoPlayNext=true; playLoopAll=true; playLoopOne=false; _ga=GA1.2.1940168918.1541896043; _gac_UA-273986-1=1.1547164360.Cj0KCQiApvbhBRDXARIsALnNoK2RKvYZc80J_RpXn3Jb4LU7QHBrpr25Cu65uBSfVcZxKw7M1GzuEkcaAu8qEALw_wcB; _gcl_aw=GCL.1547606435.~Cj0KCQiApvbhBRDXARIsALnNoK2RKvYZc80J_RpXn3Jb4LU7QHBrpr25Cu65uBSfVcZxKw7M1GzuEkcaAu8qEALw_wcB; fbm_414296278689656=base_domain=.nhaccuatui.com; nctads_ck=1nljhm822jsa92l9i268099up_1551140815432; NCTNPLV=bd2b3212fdbcbecbcee0e61c1e30af20; NCT_AUTH_JWT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTQyMTM5MDEsImxvZ2luTWV0aG9kIjoiMiIsInVzZXJJZCI6Ijg1MzMzMDUiLCJuYmYiOjE1NTE2MjE5MDEsImlhdCI6MTU1MTYyMTkwMSwiZGV2aWNlSWQiOiI4MDVCQ0MyNDY0Qjk0NkIxQTNCNjVFQjgyRjE3RkJGNCJ9.Sw8fKHUdKl9O6WGYq3CYRh28375ydPO5-4z7w-D_ik4; NCT_PAYMENT_AUTORENEW=new; NCT_ONOFF_ADV=1; NCT_AUTH=; NCTNPLP=a3ea07fc2d6effdd3a85e501605ed9bd12c11768d967c37df7619909317d4d18; __utmz=157020004.1552358143.97.38.utmcsr=nhaccuatui.com|utmccn=(referral)|utmcmd=referral|utmcct=/bai-hat/bai-hat-moi-nhat.2.html; NCT_BALLOON_INDEX-hoanvu1990=true; __utma=157020004.1940168918.1541896043.1552358143.1552435830.98; __utmc=157020004; autoPlayNext=true; NCTNPLS=694ef28e54da8dbb294f637ea6354a6b; NCTCRLS=a96bb374287c68776a3e799147fac7f0d5af6cb3b1d44c8f994de3955845e5340b55426eed9e02e206186b8e8b1bced3eb20c6b1f6b0a456f9b9a783f649100c96811a72690b4d6242915ac751a96a78c27f31bbc7d2df91442bd4b30d2f4edf7448f2812f9016efecd02319e5bba87a502d1c1d4f3784b33762f49121dcdf326fe087b2a1f9249493dc24815452778cc12c72780202fa4fc1a5fa169027bd314aa26eb9548937ebd4894c4aa53fa84e46de4bc73fe0b7878dae07a7650253074efe8795ebb24477dc9d9c2bbb8c580c39bb971a40478b6626bfe32cdb2d09473ddc6e5b8ff90bd6684dd102e9a9ad0f; __utmb=157020004.20.9.1552436738054; touchEnable=true'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'accept-endcoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': cookies
        }
        body = requests.get(downloadlink, headers=headers)
        songinfodata: dict = json.loads(body._content)
        songinfodata['data']['lyric_text'] = formatlyric
        songinf: SongInfo = NctSongInfo(songinfodata['data'])
        return songinf

    def get_songinfo(self):
        return self.songinfo.toJSON()

    def getdownload(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        localmp3file = self.get_mp3file(outputdir)
        locallyricfile = self.get_lyric(outputdir)
        songinfo.songfile = localmp3file
        songinfo.lyric = locallyricfile
        return songinfo.toJSON()

    def get_mp3file(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        mp3file = requests.get(songinfo.songfile, allow_redirects=True)
        localmp3file = os.path.join(outputdir, '{}_{}.mp3'.format(songinfo.title, songinfo.singer)).encode('utf-8')
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

    def get_lyric_text(self):
        pass


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://m.nhaccuatui.com/bai-hat/alone-alan-walker.dPAWTe6nAnZ8.html'
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
