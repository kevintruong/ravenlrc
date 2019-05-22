import abc
import codecs
import os

import requests
from bs4 import BeautifulSoup

from backend.db.ravdb import RavSongDb
from backend.storage.content import SongFile, CachedContentDir
from backend.type import SongInfo
from backend.utility.Utility import only_latin_string, get_media_info
from crawler.rc4_py3 import decrypt


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
            if keyvalue == 'timeleng':
                self.timeleng = nctsonginfo[keyvalue]
        self.id = self.get_nct_id(self.info)

    def get_nct_id(self, ncturl: str):
        nct_url = ncturl.split('.')
        return nct_url[3]

    def verify_info(self):
        self.songfile = SongFile.get_cachedfile(fid=self.songfile)


class NctCrawler(Crawler):
    nctWmUrl = "https://www.nhaccuatui.com/bai-hat/"
    nctLinkInfo = "https://www.nhaccuatui.com/ajax/get-media-info?key1={}&key2=&key3=&ip=123.23.58.251"
    songkey = r'songencryptkey=\"([a-zA-Z0-9]*)\"'
    key = "Lyr1cjust4nct"

    def __init__(self, ncturl: str):

        self.vipcookies = {
            'authority': 'www.nhaccuatui.com',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'referer': 'https://www.nhaccuatui.com/playlist/top-100-pop-usuk-hay-nhat-va.zE23R7bc8e9X.html?st=30',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'volume=29; volumeMute=0; qualityPlayerMp3=high; showAudioAds=6; fbm_414296278689656=base_domain=.nhaccuatui.com; NCT_PAYMENT_AUTORENEW=new; playLoopAll=true; playLoopOne=false; _ga=GA1.2.1165531668.1554856257; autoPlayNext=true; NCTNPLV=f0a6a3dfa83823b4bc2821166555f1d6; __utma=157020004.1165531668.1554856257.1557156288.1557978648.51; __utmz=157020004.1557978648.51.11.utmcsr=nhaccuatui.com|utmccn=(referral)|utmcmd=referral|utmcct=/mua-nhaccuatui-vip.html; PaymentPageATM=49000; nctads_ck=1hua77rq9ze50108p0hrvc15k2_1558320059165; _gid=GA1.2.1758008811.1558320060; NCT_AUTH_JWT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NjA5MzQzMTEsImxvZ2luTWV0aG9kIjoiMiIsInVzZXJJZCI6IjM1MDA3NTY2IiwibmJmIjoxNTU4MzQyMzExLCJpYXQiOjE1NTgzNDIzMTEsImRldmljZUlkIjoiNTIzNUQ4OEEzMTkwNDkyNTlFOEFDNDU1MDFBMzBBMTYifQ.H8NauyK0p5TQ5yq8Ik7kDF4Z-EKWbSOHNWai5BLwVfo; qualityPlayerVideo=highest; qualityPlayerMp3=high; NCT_ONOFF_ADV=1; NCT_BALLOON_INDEX-kevinraven=true; NCTNPLP=2d0307e07353a607ad43ba332e194e537b0259b7c0e7e5e8b95b7ddaf6d1009e; NCTNPLS=3dabf734a0e6bb5aefcda6e50a4e8ae6; NCTCRLS=fe4f03b0d998d4f5f830a247d0c82e4e54a37af95316ee4292e7211b9ce1a05eac462215ec3eb1b20b58b0e6cad1fe79b75e008ffc7b4cdc0149a8fa63c1b3c77284f57712b42be588f91e2f559c4312a2af4623fb6b79566fb7ee622adf4b03d4d524e4db703cb6dfda114b7413f6662deb6688a56d6ff524fac763c9b8cd582d1bccd85f6b4cff6ac13d665a360e118212c74818a5c879efed3f566f954055b8e3e6b977c986264aa84c9d4f012f9945fb1aadbd0dc2b534267ecac9b0f5a4a5ee483b352972d92643bd800fd1b168cea4fe11ab425551f814d383eab755395a4e5ba5991cb06ceae94afdeb799163; autoPlayNext=true; c08ef=5d86e9a80bbec6accb7d5630a55; _gat_gtag_UA_273986_1=1; JSESSIONID=rl7enke8t8wwsunf8vbwbi17; 8ff99=983433c74592ea5722db7eb6ef5',
        }

        self.proxies = {
            "http": "http://103.56.157.63:8899",
            "https": "http://103.56.157.63:8899"
        }
        if self.nctWmUrl not in ncturl:
            songinfos = ncturl.split("/")
            songid = songinfos[4]
            self.mobileNctWmUrl = NctCrawler.nctWmUrl + '{}'.format(songid)
        else:
            self.mobileNctWmUrl = ncturl
            songid = ncturl.split(".")[3]
        items = RavSongDb().get_info_by_id(songid)
        self.iscached = False
        if items:
            self.songinfo: SongInfo = SongInfo(items)
            if self.songinfo.verify_info():
                self.iscached = True
            else:
                self.songinfo = self.parser()
        else:
            print('[Warning] crawl data {}'.format(self.mobileNctWmUrl))
            self.songinfo = self.parser()

    def db_update_song_meta_info(self):
        if self.songinfo:
            RavSongDb().insert_song(self.songinfo.__dict__)

    @classmethod
    def get_nct_songid(cls, ncturl: str):
        try:
            songid = ""
            if cls.nctWmUrl not in ncturl:
                songinfos = ncturl.split("/")
                songid = songinfos[4]
                cls.mobileNctWmUrl = NctCrawler.nctWmUrl + '{}'.format(songid)
            else:
                cls.mobileNctWmUrl = ncturl
                songid = ncturl.split(".")[3]
            return songid
        except Exception as exp:
            print('can not get songid from the url {}'.format(ncturl))
            return None

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
        fields = ['title', 'creator', 'location', 'locationHQ', 'info', 'lyric', 'key']
        doc_el = BeautifulSoup(xml_text, 'xml')
        songinfo = SongInfo()
        for each_fields in fields:
            var = [el.text for el in doc_el.findAll(each_fields)]
            if len(var):
                value: str = var[0].replace('\n', '').replace('  ', '')
                if each_fields == 'title':
                    songinfo.title = value
                if each_fields == 'creator':
                    songinfo.singer = value
                if each_fields == 'location':
                    songinfo.songfile = value
                if each_fields == 'locationHQ':
                    if value:
                        songinfo.songfile = value
                if each_fields == 'lyric':
                    songinfo.lyric = value
                if each_fields == 'key':
                    songinfo.id = value
                if each_fields == 'info':
                    songinfo.info = value
        return songinfo

    def parser(self):
        try_count = 0
        while True:
            try:
                crawler = requests.get(self.mobileNctWmUrl, headers=self.vipcookies,
                                       proxies=self.proxies, verify=False)
                if crawler.status_code != 200:
                    print("status code {}".format(crawler.status_code))
                    try_count = try_count + 1
                    if try_count > 5:
                        break
                    continue
                song_xml = self.get_song_xml_file(crawler.text)
                song_info = requests.get(song_xml,
                                         headers=self.vipcookies,
                                         proxies=self.proxies,
                                         verify=False)
                soup = BeautifulSoup(crawler.text, 'html')
                lyric_text = soup.find(attrs={'class': 'pd_lyric trans', 'id': 'divLyric'}).text
                formatlyric = self.reformat_lyric(lyric_text)
                songinf = self.song_info_xml_parser(song_info.text)
                songinf.lyrictext = formatlyric
                return songinf
            except Exception as exp:
                if try_count < 5:
                    try_count = try_count + 1
                    print("{}".format(exp))
                    continue
                else:
                    raise ConnectionError('Error when when crawler data')
        raise ConnectionError('Error when when crawler data')

    def get_songinfo(self):
        return self.songinfo.toJSON()

    def getdownload(self, outputdir: str):
        songinfo: SongInfo = self.songinfo
        if not self.iscached:
            try:
                localmp3file = self.get_mp3file(outputdir)
                songinfo.songfile = localmp3file
            except Exception as exp:
                print('[ERROR] can not down load mp3 file : {}'.format(exp))
                songinfo.songfile = None
            try:
                locallyricfile = self.get_lyric(outputdir)
                songinfo.lyric = locallyricfile
            except Exception as exp:
                songinfo.lyric = None
        return songinfo

    def get_mp3file(self, outputdir: str):
        retry = 0
        retry_max = 5
        force_redownload = False
        while True:
            try:
                songinfo: SongInfo = self.songinfo
                mp3filename = only_latin_string('{}_{}_{}'.format(songinfo.title,
                                                                  songinfo.singer,
                                                                  songinfo.id))
                mp3file = SongFile.get_cachedfile(mp3filename)
                if mp3file is None or force_redownload:
                    localmp3file = os.path.join(outputdir, '{}.mp3'.format(mp3filename))
                    mp3file = requests.get(songinfo.songfile,
                                           allow_redirects=True,
                                           timeout=60,
                                           headers=self.vipcookies,
                                           proxies=self.proxies,
                                           verify=False)
                    with open(localmp3file, 'wb') as mp3filefd:
                        mp3filefd.write(mp3file.content)
                    fileinfo = CachedContentDir.gdrive_file_upload(localmp3file)
                    mp3file = SongFile.get_cachedfile(mp3filename)
                    fileid = fileinfo['id']
                else:
                    fileid = mp3file.fileinfo['id']

                if self.songinfo.timeleng is None:
                    songfile = mp3file.get()
                    self.songinfo.timeleng = get_media_info(songfile)
                if self.songinfo.timeleng is None or self.songinfo.timeleng == 0:
                    force_redownload = True
                    continue
                return fileid
            except Exception as exp:
                retry = retry + 1
                if retry > retry_max:
                    raise Exception(
                        'can not get mp3 file from the url {} - root exp {} '.format(self.songinfo.info, exp))
                else:
                    continue

    def get_lyric(self, outputdir: str):
        try:
            songinfo: SongInfo = self.songinfo
            filename = '{}_{}'.format(songinfo.title, songinfo.id)
            filename = only_latin_string(filename)
            filename = "{}.lrc".format(filename)
            lyricfile = SongFile.get_cachedfile(filename)
            if not lyricfile:
                locallyricfile = os.path.join(outputdir, filename)
                lyricfile = requests.get(songinfo.lyric,
                                         allow_redirects=True,
                                         proxies=self.proxies,
                                         verify=False)
                returndata = decrypt(NctCrawler.key, lyricfile.content)
                with codecs.open(locallyricfile, 'w', "utf-8") as f:
                    f.write(returndata)
                fileid = CachedContentDir.gdrive_file_upload(locallyricfile)
                return fileid['id']
            return lyricfile.fileinfo['id']
        except Exception as exp:
            raise Exception('can not get lyric file from the url {} exp {} '.format(self.songinfo.info, exp))


import unittest


class testnctcrawler(unittest.TestCase):
    def setUp(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/on-my-way-alan-walker-ft-sabrina-carpenter-ft-farruko.4mS3RM4QWrvb.html'
        self.nct = NctCrawler(self.url)

    def test_init(self):
        self.assertEqual(self.nct.mobileNctWmUrl,
                         NctCrawler.nctWmUrl + "nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")

    def test_parse(self):
        print(self.nct.get_songinfo())
        print('end')

    def test_download_file(self):
        self.url = r'https://www.nhaccuatui.com/bai-hat/7-rings-ariana-grande.6jZz4fuWkTt3.html'
        self.nct = NctCrawler(self.url)
        jsondat = self.nct.getdownload('/tmp/raven/cache/Song')
        print("{}".format(jsondat.toJSON()))
        self.nct.db_update_song_meta_info()

    def test_get_lyric(self):
        jsonfile = self.nct.get_lyric()
        print(jsonfile)

    def test_get_mp3file(self):
        jsonfile = self.nct.get_mp3file('./test/')
        print(jsonfile)

    def test_get_song_info(self):
        songinfo = self.nct.songinfo
        info = [songinfo.id, songinfo.title, songinfo.singer, songinfo.info]
        print(info)

    def test_request_proxy(self):
        # proxies = {
        #     "http": "http://localhost:8080",
        #     "https": "http://localhost:8080"
        # }
        proxies = {
            "http": "http://103.56.157.63:8899",
            "https": "http://103.56.157.63:8899"
        }
        # auth = HTTPProxyDigestAuth("kevin", "ravtech")
        ret = requests.get('https://www.nhaccuatui.com/playlist/top-100-pop-usuk-hay-nhat-va.zE23R7bc8e9X.html',
                           proxies=proxies, verify=False)
        print(ret.status_code)
        pass
