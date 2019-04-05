import abc
from threading import Thread

from crawler.nct import NctCrawler, SongInfo
from render.type import *
from render.type import Background
from backend.utility.Utility import *


class Cmder:
    def __init__(self):
        # self.effect: BgEffect = None
        self.background: Background = None

    @abc.abstractmethod
    def run(self):
        pass


class CrawlCmder(Cmder):
    def __init__(self, crawlcmd: dict):
        super().__init__()
        for key in crawlcmd.keys():
            if 'url' == key:
                self.url = crawlcmd[key]
            if 'output' == key:
                self.output = crawlcmd['output']
            else:
                self.output = ContentDir.SONG_DIR

    def crawl_parser(self):
        if 'nhaccuatui' in self.url:
            return NctCrawler(self.url)

    def run(self):
        crawler = self.crawl_parser()
        return crawler.getdownload(self.output)
        pass


class RenderThread(Thread):
    def __init__(self, postdata):
        super().__init__()
        self.postdata = postdata

    def run(self) -> None:
        from render.engine import BackgroundsRender
        songapi = SongApi(self.postdata)
        song_render = BackgroundsRender(songapi)
        ret = song_render.run()


class SongApi:
    def __init__(self, jsondata: dict):
        super().__init__()
        self.watermask = None
        self.song = None
        self.song_url = None
        self.rendertype = RenderType()
        self.title = None
        self.watermask = None
        self.spectrum = None
        self.lyric = None
        for keyvalue in jsondata.keys():
            if keyvalue == 'song_url':
                self.song_url = jsondata[keyvalue]
            if keyvalue == 'song':
                self.song = SongInfo(jsondata[keyvalue])
            if keyvalue == 'backgrounds':
                self.backgrounds = self.get_list_background(jsondata[keyvalue])
            if keyvalue == 'spectrum':
                self.spectrum = Spectrum(jsondata[keyvalue])
            if keyvalue == 'title':
                self.title = Title(jsondata[keyvalue])
            if keyvalue == 'watermask':
                self.watermask = WaterMask(jsondata[keyvalue])
            if keyvalue == 'lyric':
                self.lyric = Lyric(jsondata[keyvalue])
            if keyvalue == 'rendertype':
                self.rendertype = RenderType(jsondata[keyvalue])
            if keyvalue == 'song_effect':
                self.song_effect = PyJSON(jsondata[keyvalue])
        self.get_song_info_from_url()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_song_info_from_url(self):
        if self.song is None and self.song_url:
            crawlerdict = {'url': self.song_url}
            crawler = CrawlCmder(crawlerdict)
            self.song: SongInfo = SongInfo(json.loads(crawler.run()))
            pass

    def get_list_background(self, info: list):
        backgrounds = []
        for background_info in info:
            background = Background(background_info)
            backgrounds.append(background)
        return backgrounds


class layer:
    def __init__(self):
        pass
