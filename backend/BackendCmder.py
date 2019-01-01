import abc

from backend.render.ffmpegcli import FfmpegCli
from backend.crawler.subcrawler import *
from backend.subeffect.asseditor import *
from backend.subeffect.asseffect.LyricEffect import LyricEffect
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
        for keyfield in bginfo.keys():
            if 'bg_file' in keyfield:
                self.bg_file = bginfo[keyfield]
            if 'lyric_info' in keyfield:
                self.subinfo: SubtitleInfo = SubtitleInfo(bginfo[keyfield])
            if 'title_info' in keyfield:
                self.titleinfo = TitleInfo(bginfo[keyfield])


class EffectInfo:
    def __init__(self, effinfo: dict):
        self.affect_file = effinfo['affect_file']
        self.opacity = effinfo['opacity']


class BuildCmder(Cmder):

    def run(self):
        if self.build_type == BuildType.BUILD_PREVIEW:
            return self.build_preview()
        elif self.build_type == BuildType.BUILD_RELEASE:
            return self.build_release()
        pass

    def __init__(self, cmd: dict):
        super().__init__()
        for field in cmd.keys():
            if 'type' in field:
                self.build_type = BuildType(cmd[field])
            if 'song_info' in field:
                self.songinfo = SongInfo(cmd[field])
            if 'background_info' in field:
                self.bginfo = BackgroundInfo(cmd[field])
            if 'effect_info' in field:
                self.effectinfo = EffectInfo(cmd[field])
            if 'lyric_effect' in field:
                self.lyric_effect = LyricEffect(cmd[field])
            if 'output' in field:
                self.output = cmd[field]
            self.ffmpegcli = FfmpegCli()
            self.time_length = self.ffmpegcli.get_media_time_length(self.songinfo.location)

    def build_mv(self, profile):
        preview_profile = profile

        self.ffmpegcli.set_resolution(preview_profile)
        preview_asstempfile = AssTempFile().getfullpath()
        preview_bgtempfile = PngTempFile().getfullpath()

        create_ass_from_lrc(self.songinfo.lyric,
                            preview_asstempfile,
                            self.bginfo.subinfo,
                            preview_profile)
        if self.lyric_effect is not None:
            # TODO add process lyric effect
            pass

        time_length = self.ffmpegcli.get_media_time_length(self.songinfo.location) / 2

        preview_affect = AffMvTemplateFile().getfullpath()
        logger.debug(preview_profile)
        if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
            self.ffmpegcli.scale_input(self.bginfo.bg_file,
                                       preview_profile,
                                       preview_bgtempfile)
            self.ffmpegcli.scale_input(self.effectinfo.affect_file,
                                       preview_profile,
                                       preview_affect)

        else:
            preview_affect = self.effectinfo.affect_file
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
                                           self.effectinfo.opacity)
        preview_bg_aff_sub_mv = MvTempFile().getfullpath()
        self.ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                           preview_bg_affect_mv,
                                           preview_bg_aff_sub_mv)
        self.ffmpegcli.mux_audio_to_video(preview_bg_aff_sub_mv,
                                          self.songinfo.location,
                                          self.output
                                          )

        pass

    def build_preview(self):
        return self.build_mv(FFmpegProfile.PROFILE_LOW.value)

    def build_release(self):
        return self.build_mv(FFmpegProfile.PROFILE_2K.value)
