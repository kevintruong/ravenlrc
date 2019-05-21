import os

from threading import Thread

from backend.db.ravdb import RavSongDb
from backend.type import SongInfo
from crawler.nct import NctCrawler
from render.cache import CachedContentDir


class CrawlCmder(Thread):
    def __init__(self, crawlcmd: dict):
        super().__init__()
        self.output = None
        for key in crawlcmd.keys():
            if 'url' == key:
                self.url = crawlcmd[key]
            if 'output' == key:
                self.output = crawlcmd['output']
        if self.output is None:
            self.output = CachedContentDir.SONG_DIR

    def crawl_parser(self):
        if 'nhaccuatui' in self.url:
            songid = NctCrawler.get_nct_songid(self.url)
            songitem = RavSongDb().get_info_by_id(songid)
            if songitem:
                songinfo = SongInfo(songitem)
                return songinfo
            else:
                return None

    def get_parser(self):
        if 'nhaccuatui' in self.url:
            return NctCrawler(self.url)
        else:
            raise NotImplementedError('not support the {}'.format(self.url))

    @classmethod
    def get_link(cls, link):
        if 'nhaccuatui' in link:
            if 'bai-hat-moi.html' in link:
                return None
            if 'top-20.nhac-viet.html' in link:
                return None
            songid = NctCrawler.get_nct_songid(link)
            songitem = RavSongDb().get_info_by_id(songid)
            if songitem:
                songinfo = SongInfo(songitem)
                return songinfo
            else:
                crawlerthread = CrawlCmder({'url': link})
                crawlerthread.start()
                return crawlerthread

    def run(self):
        try:
            songinfo = self.crawl_parser()
            if songinfo:
                return songinfo
            else:
                crawler = self.get_parser()
                songinfo = crawler.getdownload(self.output)
                RavSongDb().insert_song(songinfo.__dict__)
                return songinfo
        except Exception as exp:
            print('ignore the exceptiion {}'.format(exp))
            raise exp


import unittest


class Test_SongCrawler(unittest.TestCase):

    def test_crawl_newsong(self):
        song_url = {
            'url': r'https://www.nhaccuatui.com/bai-hat/on-my-way-alan-walker-ft-sabrina-carpenter-ft-farruko.4mS3RM4QWrvb.html'
        }
        crawlercmd = CrawlCmder(song_url)
        crawlercmd.run()
        pass


class Test_Crawler(unittest.TestCase):
    CurDir = os.path.dirname(os.path.realpath(__file__))

    def setUp(self) -> None:
        self.songfiles = open(os.path.join(self.CurDir, 'song.txt'), 'r')

    def test_run(self):
        threads = []
        enable = False
        for cnt, line in enumerate(self.songfiles):
            try:
                crawler = CrawlCmder.get_link(line.rstrip())
                if crawler is None:
                    continue
                if type(crawler) is not str:
                    threads.append(crawler)
                    if len(threads) > 2:
                        enable = False
                        while True:
                            for index, threaditem in enumerate(threads):
                                if not threaditem.isAlive():
                                    threads.remove(threaditem)
                                    print('thread lends {}'.format(len(threads)))
                                    enable = True
                            if enable:
                                break
            except Exception as exp:
                print(exp)

    def test_get_songinfo(self):
        crawler = CrawlCmder.get_link('https://www.nhaccuatui.com/bai-hat/tim-ve-noi-dau-y-kroc.JVHiWTEfHeum.html')
        print(crawler)


if __name__ == '__main__':
    songfiles = open('/mnt/Data/Project/ytcreatorservice/crawler/song.txt', 'r')
    for cnt, line in enumerate(songfiles):
        try:
            print('[COUNT] {} crawl : {}'.format(cnt, line))
            crawler = CrawlCmder(
                {'url': line.rstrip()})
            songinfo = crawler.run()
            print(songinfo)
        except Exception as exp:
            print(exp)
