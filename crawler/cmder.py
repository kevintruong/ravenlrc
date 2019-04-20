import os

from time import sleep

from backend.type import Cmder
from crawler.db.helper import GdriveSongInfoDb
from crawler.nct import NctCrawler
from render.cache import CachedContentDir
from threading import Thread


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
            return NctCrawler(self.url)

    @classmethod
    def check_link(cls, link):
        if 'nhaccuatui' in link:
            if 'bai-hat-moi.html' in link:
                return None
            if 'top-20.nhac-viet.html' in link:
                return None
            nctParser = NctCrawler(link)
            if nctParser.iscached:
                return None
            else:
                return CrawlCmder({'url': link})

    def run(self):
        try:
            crawler = self.crawl_parser()
            statuas = crawler.getdownload(self.output)
            return statuas
        except Exception as exp:
            print('ignore the exceptiion {}'.format(exp))


import unittest


class Test_Crawler(unittest.TestCase):
    CurDir = os.path.dirname(os.path.realpath(__file__))

    def setUp(self) -> None:
        self.songfiles = open(os.path.join(self.CurDir, 'song.txt', 'r'))

    def test_run(self):
        threads = []
        enable = False
        for cnt, line in enumerate(self.songfiles):
            try:
                crawler = CrawlCmder.check_link(line.rstrip())
                if crawler:
                    threads.append(crawler)
                    crawler.start()
                    if len(threads) > 50:
                        enable = False
                        while True:
                            for index, threaditem in enumerate(threads):
                                if not threaditem.isAlive():
                                    threads.remove(threaditem)
                                    print('thread lends {}'.format(len(threads)))
                                    enable = True
                            if enable:
                                break
                            else:
                                sleep(0.5)
            except Exception as exp:
                print(exp)


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
