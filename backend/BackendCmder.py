from enum import Enum, IntEnum

import json5

from backend.render.cache import ContentDir, EffectCachedFile, MuxAudioVidCachedFile, BgEffectCachedFile, \
    BgImgCachedFile, BgVidCachedFile
from backend.render.type import Size, Position, Font
from backend.crawler.nct import *
from backend.crawler.subcrawler import *
from backend.render.ffmpegcli import FfmpegCli
from backend.subeffect.asseditor import *
from backend.subeffect.asseffect.LyricEffect import LyricEffect
from backend.utility.Utility import check_file_existed, generate_mv_filename, PyJSON


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


class BuildType(IntEnum):
    BUILD_PREVIEW = 0
    BUILD_RELEASE = 1


class RenderTypeCode(Enum):
    BUILD_PREVIEW = "preview"
    BUILD_RELEASE = "release"


class Rectangle:
    def __init__(self, coordinate: list):
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.w = coordinate[2]
        self.h = coordinate[3]


class TitleInfo(LyricConfigInfo):

    def __init__(self, titleinfo: dict):
        super().__init__(titleinfo)


class BackgroundInfo:
    def __init__(self, bginfo: dict):
        for keyfield in bginfo.keys():
            if 'bg_file' in keyfield:
                self.bg_file = ContentDir.get_file_path(ContentDir.BGIMG_DIR.value, bginfo[keyfield])
                check_file_existed(self.bg_file)
            if 'lyric_info' in keyfield:
                self.subinfo: LyricConfigInfo = LyricConfigInfo(bginfo[keyfield])
            if 'title_info' in keyfield:
                self.titleinfo = TitleInfo(bginfo[keyfield])


class Lyric:
    def __init__(self, info: dict):
        self.file = None
        # self.effect = None
        self.words = []
        if 'file' in info:
            self.file = info['file']
        if 'words' in info:
            for wordeffect in info['words']:
                self.words.append(LyricEffect(wordeffect))
        pass


class Spectrum(PyJSON):
    def __init__(self, d):
        self.templatecode = None
        self.custom = None
        super().__init__(d)


class BgSpectrum:
    def __init__(self, info: dict):
        for keyvalue in info.keys():
            if keyvalue == 'position':
                self.position = Position(info[keyvalue])
            if keyvalue == 'size':
                self.size = Size(info[keyvalue])


class BgEffect:
    def __init__(self, info: dict):
        self.file = ContentDir.get_file_path(ContentDir.EFFECT_DIR.value, info['file'])
        check_file_existed(self.file)
        self.opacity = int(info['opacity'])
        pass


class BgTitle:
    def __init__(self, cmd: dict):
        self.file = cmd['file']
        self.position = Position(cmd['position'])


class BgWaterMask:
    def __init__(self, info: dict):
        self.file = info['file']
        self.position = Position(info['position'])


class BgLyric:
    def __init__(self, info: dict):
        if 'position' in info:
            self.position = Position(info['position'])
        if 'size' in info:
            self.size = Size(info['size'])
        if 'font' in info:
            self.font = Font(info['font'])


class Title(PyJSON):
    def __init__(self, d):
        super().__init__(d)


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


class EffectInfo:
    def __init__(self, effinfo: dict):
        self.file = ContentDir.get_file_path(ContentDir.EFFECT_DIR.value, effinfo['file'])
        check_file_existed(self.file)
        self.opacity = effinfo['opacity']


class Resolution(Size):

    def __init__(self, info: dict):
        super().__init__(info)


class RenderConfigure:
    def __init__(self, info: dict):
        for keyvalue in info.keys():
            if keyvalue == 'duration':
                self.duration = info[keyvalue]
            if keyvalue == 'resolution':
                self.resolution = Resolution(info[keyvalue])


class RenderType:
    def __init__(self, info=None):
        if info:
            for keyvalue in info.keys():
                if keyvalue == 'type':
                    self.type = info[keyvalue]
                if keyvalue == 'config':
                    self.configure = RenderConfigure(info[keyvalue])
        else:
            self.type = 'preview'
            self.configure = RenderConfigure({'duration': 90,
                                              'resolution': {'width': 1280, 'height': 720}
                                              })


class MusicVideoKind(IntEnum):
    ALBUM_SINGLE_BACKGROUND = 0
    ALBUM_MULTI_BACKGROUND = 1
    MV_MULTI_BACKGROUND = 2
    MV_SINGLE_BACKGROUND = 3


class SongApi:
    song_urls: str

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
