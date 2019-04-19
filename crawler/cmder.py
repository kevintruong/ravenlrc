from backend.type import Cmder
from crawler.db.helper import GdriveSongInfoDb
from crawler.nct import NctCrawler
from render.cache import CachedContentDir


class CrawlCmder(Cmder):
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

    def run(self):
        crawler = self.crawl_parser()
        return crawler.getdownload(self.output)
        pass


import unittest


class Test_Crawler(unittest.TestCase):
    def setUp(self) -> None:
        self.songfiles = open('/tmp/song.txt', 'r')

    def test_run(self):
        for cnt, line in enumerate(self.songfiles):
            try:
                print('[COUNT] {} crawl : {}'.format(cnt,line))
                self.crawler = CrawlCmder(
                    {'url': line.rstrip()})
                songinfo = self.crawler.run()
                print(songinfo)
            except Exception as exp:
                print(exp)


if __name__ == '__main__':
    songfiles = open('/tmp/song.txt', 'r')
    for cnt, line in enumerate(songfiles):
        try:
            print('[COUNT] {} crawl : {}'.format(cnt,line))
            crawler = CrawlCmder(
                {'url': line.rstrip()})
            songinfo = crawler.run()
            print(songinfo)
        except Exception as exp:
            print(exp)


