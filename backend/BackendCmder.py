import json
from enum import Enum, IntEnum
import abc

from backend.ffmpeg.ffmpegcli import FfmpegCli, FFmpegProfile
from backend.subcraw.subcrawler import *
from backend.TempFileMnger import *
from backend.subcraw.asseditor import *


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


class Rectangle:
    def __init__(self, coordinate: list):
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.w = coordinate[2]
        self.h = coordinate[3]


class TitleInfo(SubtitleInfo):

    def __init__(self, titleinfo: dict):
        super().__init__(titleinfo)


class BackgroundInfo:
    def __init__(self, bginfo: dict):
        self.bg_file = bginfo['bg_file']
        self.subinfo: SubtitleInfo = SubtitleInfo['sub_info']
        self.titleinfo = TitleInfo['title_info']


class AffectInfo:
    def __init__(self, affinfo: dict):
        self.affect_file = affinfo['affect_file']
        self.opacity = affinfo['opacity']


class BuildCmder(Cmder):

    def run(self):
        if self.build_type == BuildType.BUILD_PREVIEW:
            return self.build_preview()
        elif self.build_type == BuildType.BUILD_RELEASE:
            return self.build_release()
        pass

    def __init__(self, cmd: dict):
        super().__init__()
        self.build_type = BuildType(cmd['type'])
        self.songinfo = SongInfo(cmd['song_info'])
        self.bginfo = BackgroundInfo(cmd['background_info'])
        self.affinfo = AffectInfo(cmd['affect_info'])
        self.ffmpegcli = FfmpegCli()
        self.time_length = self.ffmpegcli.get_media_time_length(self.songinfo.song_file)

    def build_preview(self):
        self.ffmpegcli.set_resolution(FFmpegProfile.PROFILE_LOW.value)
        preview_asstempfile = AssTempFile().getfullpath()
        preview_bgtempfile = PngTempFile().getfullpath()

        create_ass_subtitle(self.songinfo.lyric_file,
                            preview_asstempfile,
                            self.bginfo.subinfo,
                            FFmpegProfile.PROFILE_LOW.value)

        preview_bgtempfile = self.ffmpegcli.scale_input(self.bginfo.bg_file,
                                                        FFmpegProfile.PROFILE_LOW.value,
                                                        preview_bgtempfile)
        time_length = self.ffmpegcli.get_media_time_length(self.songinfo.song_file) / 2

        bgmv = BgMvTemplateFile().getfullpath()
        bgmv = self.ffmpegcli.create_media_file_from_img(preview_bgtempfile, time_length, bgmv)
        affectmv = AffMvTemplateFile().getfullpath()
        affectmv = self.ffmpegcli.scale_input(self.affinfo.affect_file,
                                              FFmpegProfile.PROFILE_LOW.value,
                                              affectmv)

        pass

    def build_release(self):
        pass
