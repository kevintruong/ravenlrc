import abc

from backend.render.ffmpegcli import FfmpegCli
from backend.crawler.subcrawler import *
from backend.subeffect.asseditor import *
from backend.utility.Utility import *
from backend.crawler.nct import *


class Cmder:
    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass


class CrawlCmder(Cmder):

    def __init__(self, crawlcmd: dict):
        super().__init__()
        self.crawl_url = crawlcmd['crawl_url']
        self.output = crawlcmd['output']

    def crawl_parser(self):
        if 'nhaccuatui' in self.crawl_url:
            return NctCrawler(self.crawl_url)

    def run(self):
        crawler: Crawler = self.crawl_parser()
        return crawler.getdownload(self.output)
        pass


class BuildType(IntEnum):
    BUILD_PREVIEW = 0
    BUILD_RELEASE = 1


class SongInfo:
    def __init__(self, songinfo: dict):
        self.song_file = songinfo['song_file']
        check_file_existed(self.song_file)
        self.lyric_file = songinfo['lyric_file']
        check_file_existed(self.lyric_file)
        self.song_name = songinfo['song_name']
        self.title_file = songinfo['title_file']
        check_file_existed(self.title_file)


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
        self.subinfo: SubtitleInfo = SubtitleInfo(bginfo['sub_info'])
        self.titleinfo = TitleInfo(bginfo['title_info'])


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
        self.output = cmd['output']
        self.ffmpegcli = FfmpegCli()
        self.time_length = self.ffmpegcli.get_media_time_length(self.songinfo.song_file)

    def build_mv(self, profile):
        preview_profile = profile

        self.ffmpegcli.set_resolution(preview_profile)
        preview_asstempfile = AssTempFile().getfullpath()
        preview_bgtempfile = PngTempFile().getfullpath()

        create_ass(self.songinfo.lyric_file,
                   preview_asstempfile,
                   self.bginfo.subinfo,
                   FFmpegProfile.PROFILE_LOW.value)

        time_length = self.ffmpegcli.get_media_time_length(self.songinfo.song_file) / 2

        preview_affect = AffMvTemplateFile().getfullpath()
        logger.debug(preview_profile)
        if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
            self.ffmpegcli.scale_input(self.bginfo.bg_file,
                                       preview_profile,
                                       preview_bgtempfile)
            self.ffmpegcli.scale_input(self.affinfo.affect_file,
                                       preview_profile,
                                       preview_affect)

        else:
            preview_affect = self.affinfo.affect_file
            preview_bgtempfile = self.bginfo.bg_file

        preview_bgmv = BgMvTemplateFile().getfullpath()
        self.ffmpegcli.create_media_file_from_img(preview_bgtempfile, time_length, preview_bgmv)

        preview_affectmv = AffMvTemplateFile().getfullpath()
        self.ffmpegcli.create_background_affect_with_length(preview_affect,
                                                            time_length,
                                                            preview_affectmv)
        preview_bg_affect_mv = MvTempFile().getfullpath()
        self.ffmpegcli.add_affect_to_video(preview_bgmv,
                                           preview_affectmv,
                                           preview_bg_affect_mv,
                                           self.affinfo.opacity)
        preview_bg_aff_sub_mv = MvTempFile().getfullpath()
        self.ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                           preview_bg_affect_mv,
                                           preview_bg_aff_sub_mv)
        self.ffmpegcli.mux_audio_to_video(preview_bg_aff_sub_mv,
                                          self.songinfo.song_file,
                                          self.output
                                          )

        pass

    def build_preview(self):
        return self.build_mv(FFmpegProfile.PROFILE_LOW.value)

    def build_release(self):
        return self.build_mv(FFmpegProfile.PROFILE_2K.value)
