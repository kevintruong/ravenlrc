from enum import Enum, IntEnum

from backend.crawler.nct import *
from backend.render.cache import ContentDir
from backend.render.type import Lyric, Spectrum, Title, BgLyric, BgEffect, BgSpectrum, RenderType
from backend.utility.Utility import check_file_existed, PyJSON


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
                self.output = ContentDir.SONG_DIR.value
        print(self.url + self.output)

    def crawl_parser(self):
        if 'nhaccuatui' in self.url:
            return NctCrawler(self.url)

    def run(self):
        crawler: Crawler = self.crawl_parser()
        return crawler.getdownload(self.output)
        pass


class RenderTypeCode(Enum):
    BUILD_PREVIEW = "preview"
    BUILD_RELEASE = "release"


class BgTitle(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class WaterMask(PyJSON):
    def __init__(self, d):
        super().__init__(d)


class BgWaterMask(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class Background:
    def __init__(self, info: dict):
        self.file = None
        self.effect = None
        self.lyric = None
        self.title = None
        self.spectrum = None
        self.watermask = None
        self.timing = None
        for field in info.keys():
            if field == 'file':
                self.file = ContentDir.get_file_path(ContentDir.BGIMG_DIR.value, info[field])
                check_file_existed(self.file)
            elif field == 'effect':
                self.effect = BgEffect(info[field])
            elif field == 'lyric':
                self.lyric = BgLyric(info[field])
            elif field == 'watermask':
                self.watermask = BgWaterMask(info[field])
            elif field == 'title':
                self.title = BgTitle(info[field])
            elif field == 'spectrum':
                self.spectrum = BgSpectrum(info[field])
            elif field == 'timing':
                self.timing = info[field]

    pass


class MusicVideoKind(IntEnum):
    ALBUM_SINGLE_BACKGROUND = 0
    ALBUM_MULTI_BACKGROUND = 1
    MV_MULTI_BACKGROUND = 2
    MV_SINGLE_BACKGROUND = 3


class SongApi:
    def __init__(self, jsondata: dict):
        super().__init__()
        self.watermask = None
        self.song = None
        self.song_url = None
        self.rendertype = RenderType()
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
