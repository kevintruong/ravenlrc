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
            if keyvalue == 'timelength()':
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
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': 'nctads_ck=g49j2tu1f2il4w4w6x64fhof_1554856256954; fbm_414296278689656=base_domain=.nhaccuatui.com; NCT_BALLOON_INDEX=true; __utma=157020004.1165531668.1554856257.1554856257.1555640036.2; __utmc=157020004; __utmz=157020004.1555640036.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); autoPlayNext=true; NCT_AUTH_JWT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTgyMzQyMjMsImxvZ2luTWV0aG9kIjoiMiIsInVzZXJJZCI6IjM1MDA3NTY2IiwibmJmIjoxNTU1NjQyMjIzLCJpYXQiOjE1NTU2NDIyMjMsImRldmljZUlkIjoiMzI2RjQyNjE2RjFFNDUwN0FGOURDQzI0NjUwQzA2MEQifQ.HkrSQiVikuH7-Ap3uziLGILkBm-VvLACQy2bQ6LGMBQ; NCT_BALLOON_INDEX-kevinraven=true; PaymentPageATM=49000; NCT_PAYMENT_DISCOUNT=; NCT_PAYMENT_DISCOUNT_A=; NCT_PAYMENT_AUTORENEW=new; NCT_ONOFF_ADV=1; __utmt=1; NCTNPLP=a32c585f6e8f316dc3d76e6edc2443b538d4ac2314425454f9a6135c898177dc; NCTNPLS=58e5801f60974d1267f8898b44c0af16; NCTCRLS=fb30d00ae64a520529006004e982a291c977687b0ec71b995d9b3d1825eec529cab3d7adcee90884af916eb9193e1849a885b80bafbcae99849cdd6f25e8953d03f50587f73a6f8075f424d7283129c4664d563f2e3c2f19f34f35e0d98e1d84cf83f3eda9c2cd35fd9df68a92e890b0ed4cb2c8721131fa1f94214cc3d24c11f03efe89190478615b3b70a50bb3a32b262d592b918d40527c17a70549b4d3662173ab5acb841066cb2296ad0f92a6c1bc7df478c155dfac51c4a4df8a017f98a6c5d9e220fdd0e44df40b5ea314929853d760c0d412c0dcb0dfbbdb502be6fb8a9f53d395d63df48f091d379d3349eb; 80085=401d10668d97dffa38c487e85e9; JSESSIONID=1s40xulznm0gi1x28vfwijgodk; __utmb=157020004.61.9.1555642662756',
        }
        self.proxies = {
            "http": "http://kevin:ravtech@103.56.157.63:8899"
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
            self.iscached = True
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
        crawler = requests.get(self.mobileNctWmUrl, proxies=self.proxies)
        song_xml = self.get_song_xml_file(crawler.text)
        # Get song_xml -> parse
        song_info = requests.get(song_xml, headers=self.vipcookies, proxies=self.proxies)
        # song_info = ProxyRequests.get_ins().get(song_xml, headers=self.vipcookies)
        soup = BeautifulSoup(crawler.text, 'html')
        lyric_text = soup.find(attrs={'class': 'pd_lyric trans', 'id': 'divLyric'}).text
        formatlyric = self.reformat_lyric(lyric_text)
        songinf = self.song_info_xml_parser(song_info.text)
        songinf.lyrictext = formatlyric
        return songinf

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
        while True:
            try:
                songinfo: SongInfo = self.songinfo
                mp3filename = only_latin_string('{}_{}_{}'.format(songinfo.title,
                                                                  songinfo.singer,
                                                                  songinfo.id))
                mp3file = SongFile.get_cachedfile(mp3filename)
                if mp3file is None:
                    localmp3file = os.path.join(outputdir, '{}.mp3'.format(mp3filename))
                    mp3file = requests.get(songinfo.songfile,
                                           allow_redirects=True,
                                           timeout=60,
                                           headers=self.vipcookies,
                                           proxies=self.proxies)
                    with open(localmp3file, 'wb') as mp3filefd:
                        mp3filefd.write(mp3file.content)
                    self.songinfo.timeleng = get_media_info(localmp3file)
                    fileid = CachedContentDir.gdrive_file_upload(localmp3file)
                    return fileid['id']
                if self.songinfo.timeleng is None:
                    songfile = mp3file.get()
                    self.songinfo.timeleng = get_media_info(songfile)
                return mp3file.fileinfo['id']
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
                lyricfile = requests.get(songinfo.lyric, allow_redirects=True, proxies=self.proxies)
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
        self.url = r'https://www.nhaccuatui.com/bai-hat/it-aint-me-kygo-ft-selena-gomez.PPYMmjs8AgOU.html'
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
        proxies = {
            "http": "http://kevin:ravtech@103.56.157.63:8899"
        }
        # auth = HTTPProxyDigestAuth("kevin", "ravtech")
        ret = requests.get('http://www.google.com',
                           proxies=proxies)
        print(ret.status_code)
        pass
