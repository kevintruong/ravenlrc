import json
from enum import Enum, IntEnum
import abc
from backend.subcraw.subcrawler import *


class Cmder:
    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class CrawlType(IntEnum):
    CRAWL_LYRIC = 0
    CRAWL_SONG = 1
    CRAWL_LYRIC_SONG = 2


class CrawlLyricCmder(Cmder):

    def __init__(self, crawlcmd: dict):
        super().__init__()
        self.crawl_url = crawlcmd['crawl_url']
        self.output = crawlcmd['output']

    def run(self):
        crawl_lyric(self.crawl_url, self.output)
        return {'output': self.output}
        pass


class CrawlSongCmder(Cmder):

    def __init__(self, crawlcmd: dict):
        super().__init__()
        self.crawl_url = crawlcmd['crawl_url']
        self.quality = crawlcmd['audio_quality']
        self.output = crawlcmd['output']

    def run(self):
        return "Not support yet"
        download_mp3_file(self.crawl_url, self.quality, self.output)
        return {'output': self.output}
        pass


class CrawlSongLyricCmder(Cmder):

    def __init__(self, crawlcmd: dict):
        super().__init__()
        self.crawl_url = crawlcmd['crawl_url']
        self.quality = crawlcmd['audio_quality']
        self.output_lrc = crawlcmd['output_lrc']
        self.output_audio = crawlcmd['output_audio']

    def run(self):
        return "Not support yet"
        download_mp3_file(self.crawl_url, self.quality, self.output_audio)
        crawl_lyric(self.crawl_url, self.output_lrc)
        return {'output_lrc': self.output_lrc, 'output_audio': self.output_audio}
        pass


class CrawlCmder:
    CRAWL_TYPE = 'crawl_type'

    @classmethod
    def get_crawlcmder(cls, crawlcmd: dict):
        crawler_type = CrawlType(crawlcmd[cls.CRAWL_TYPE])
        if crawler_type == CrawlType.CRAWL_LYRIC:
            return CrawlLyricCmder(crawlcmd)
        if crawler_type == CrawlType.CRAWL_SONG:
            return CrawlSongCmder(crawlcmd)
        if crawler_type == CrawlType.CRAWL_LYRIC_SONG:
            return CrawlSongLyricCmder(crawlcmd)


class BuildType(IntEnum):
    BUILD_PREVIEW = 0
    BUILD_RELEASE = 1


class SongInfo:
    def __init__(self, songinfo: dict):
        self.song_file = songinfo['song_file']
        self.lyric_file = songinfo['lyric_file']
        self.song_name = songinfo['song_name']
        self.title_file = songinfo['title_file']


class Coordinate:
    def __init__(self, coordinate: list):
        self.x = coordinate[0]
        self.y = coordinate[1]


class RectSize:
    def __init__(self, rectsize: list):
        self.w = rectsize[0]
        self.h = rectsize[1]


class SubtitleInfo:
    def __init__(self, subinfo: dict):
        self.coordinate = Coordinate(subinfo['coordinate'])
        self.size = RectSize(subinfo['size'])
        self.fontname = subinfo['fontname']
        self.fontcolor = subinfo['fontcolor']
        self.fontsize = subinfo['fontsize']


class TitleInfo(SubtitleInfo):

    def __init__(self, titleinfo: dict):
        super().__init__(titleinfo)


class BackgroundInfo:
    def __init__(self, bginfo: dict):
        self.bg_file = bginfo['bg_file']
        self.subinfo = SubtitleInfo['sub_info']
        self.titleinfo = TitleInfo['title_info']


class AffectInfo:
    def __init__(self, affinfo: dict):
        self.affect_file = affinfo['affect_file']
        self.opacity = affinfo['opacity']


class BuildCmder(Cmder):

    def run(self):
        pass

    def __init__(self, cmd: dict):
        super().__init__()
        self.build_type = BuildType(cmd['type'])
        self.songinfo = SongInfo(cmd['song_info'])
        self.bginfo = BackgroundInfo(cmd['background_info'])
        self.affinfo = AffectInfo(cmd['affect_info'])
