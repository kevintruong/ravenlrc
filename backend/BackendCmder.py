from enum import Enum
from backend.crawler.nct import *
from backend.crawler.subcrawler import *
from backend.render.ffmpegcli import FfmpegCli
from backend.subeffect.asseditor import *
from backend.subeffect.asseffect.LyricEffect import LyricEffect
from backend.utility.Utility import check_file_existed, FileInfo

CurDir = os.path.dirname(os.path.realpath(__file__))
contentDir = os.path.join(CurDir, 'content')

import backend.yclogger

telelog = logging.getLogger('telebot')


class ContentDir(Enum):
    SONG_DIR = os.path.join(contentDir, 'Song')
    EFFECT_DIR = os.path.join(contentDir, 'Effect')
    TITLE_DIR = os.path.join(contentDir, 'Title')
    MVCONF_DIR = os.path.join(contentDir, 'MvConfig')
    BGIMG_DIR = os.path.join(contentDir, 'BgImage')
    MVRELEASE_DIR = os.path.join(contentDir, 'Mv/Release')
    MVPREV_DIR = os.path.join(contentDir, 'Mv/Preview')
    FONTFILES_DIR = os.path.join(contentDir, 'Font')
    BUILDCMD_DIR = os.path.join(contentDir, 'BuildCmd')

    @classmethod
    def get_file_path(cls, dir: str, filename: str):
        listfiles = os.listdir(dir)
        for file in listfiles:
            if filename in file:
                return os.path.join(dir, file)
        return None


class CachedFile:
    @classmethod
    def get_cached_profile_filename(cls, filepath: str, profile, extension=None):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        if extension:
            return name + '_' + profile + extension
        return name + '_' + profile + ext
        pass


class EffectCachedFile(CachedFile):
    CachedEffectDir = os.path.join(ContentDir.EFFECT_DIR.value, '.cache')

    @classmethod
    def get_cachedfile(cls, filename):
        listfiles = os.listdir(cls.CachedEffectDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.CachedEffectDir, file)
        return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedEffectDir, filename)


class Bg_Effect_CachedFile(CachedFile):
    CachedEffectDir = os.path.join(ContentDir.EFFECT_DIR.value, '.cache')
    BgEffectCachedDir = os.path.join(CachedEffectDir, 'BgEffect')

    @classmethod
    def get_cachedfile(cls, filename):
        listfiles = os.listdir(cls.BgEffectCachedDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.BgEffectCachedDir, file)
        return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.BgEffectCachedDir, filename)

    @classmethod
    def get_cached_file_name(cls, previewbgmv, previeweffectmv):
        bgmv_fileinfo = FileInfo(previewbgmv)
        effmv_fileinfo = FileInfo(previeweffectmv)
        bgeff_cachedfilename = bgmv_fileinfo.name + '_' + effmv_fileinfo.name + '.mp4'
        return bgeff_cachedfilename


class BgImgCachedFile(CachedFile):
    CachedDir = os.path.join(ContentDir.BGIMG_DIR.value, '.cache')

    @classmethod
    def get_cachedfile(cls, filename):
        listfiles = os.listdir(cls.CachedDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.CachedDir, file)
        return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedDir, filename)

    pass


class BgVidCachedFile(CachedFile):
    CachedBgVidDir = os.path.join(ContentDir.BGIMG_DIR.value, '.cache')

    @classmethod
    def get_cachedfile(cls, filename):
        listfiles = os.listdir(cls.CachedBgVidDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.CachedBgVidDir, file)
        return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedBgVidDir, filename)

    pass


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


class EffectInfo:
    def __init__(self, effinfo: dict):
        self.effect_file = ContentDir.get_file_path(ContentDir.EFFECT_DIR.value, effinfo['affect_file'])
        check_file_existed(self.effect_file)
        self.opacity = effinfo['opacity']


class BuildCmder(Cmder):

    def run(self):
        try:
            if self.build_type == BuildType.BUILD_PREVIEW:
                self.time_length = int(self.time_length / 2)
                self.build_preview()
            elif self.build_type == BuildType.BUILD_RELEASE:
                self.build_release()
            self.toJSON()
            return self.output

        except Exception as e:
            print("Exception as {}".format(e))
            raise e

    def auto_reconfig_build_cmd(self):
        if self.build_type is None:
            self.build_type = BuildType.BUILD_RELEASE
        pass

    def toJSON(self):
        buildfilename = "buildcmd_" + self.songinfo.title + self.build_type.name + ".json5"
        buildfilepath = os.path.join(ContentDir.BUILDCMD_DIR.value, buildfilename)
        with open(buildfilepath, 'w') as file:
            json.dump(self, file, default=lambda o: o.__dict__,
                      sort_keys=True, indent=4)

    def __init__(self, cmd: dict):
        super().__init__()
        try:
            self.songinfo = None
            self.song_url = None
            self.build_type = None
            self.bginfo = None
            self.effectinfo = None
            self.lyric_effect = None
            for field in cmd.keys():
                if 'type' in field:
                    self.build_type = BuildType(cmd[field])
                if 'song_url' in field:
                    self.song_url = cmd[field]
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
            self.get_song_info_from_url()
            self.auto_reconfig_build_cmd()
            self.time_length = self.ffmpegcli.get_media_time_length(self.songinfo.location)
            self.configure_output()
        except Exception as e:
            print("error {}".format(e))
            raise e

    def configure_output(self):
        if self.build_type == BuildType.BUILD_PREVIEW:
            self.output = os.path.join(ContentDir.MVPREV_DIR.value,
                                       self.build_type.name.lower() + '_' + self.songinfo.title + ".mp4")
        elif self.build_type == BuildType.BUILD_RELEASE:
            self.output = os.path.join(ContentDir.MVRELEASE_DIR.value,
                                       self.build_type.name.lower() + '_' + self.songinfo.title + ".mp4")

    def get_song_info_from_url(self):
        if self.songinfo is None and self.song_url:
            crawlerdict = {
                'crawl_url': self.song_url,
                'output': ContentDir.SONG_DIR.value
            }
            crawler = CrawlCmder(crawlerdict)
            self.songinfo = SongInfo(json.loads(crawler.run()))
            pass

    def build_mv(self, profile):
        preview_profile = profile

        self.ffmpegcli.set_resolution(preview_profile)
        preview_asstempfile = AssTempFile().getfullpath()
        create_ass_from_lrc(self.songinfo.lyric,
                            preview_asstempfile,
                            self.bginfo.subinfo,
                            preview_profile)

        if self.lyric_effect is not None:
            # TODO add process lyric effect
            pass

        time_length = self.time_length

        logger.debug(preview_profile)

        if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
            preview_bgtempfile = self.get_cached_backgroundimg(preview_profile)
            preview_affect = self.get_cached_effect_file(preview_profile)
        else:
            preview_affect = self.effectinfo.effect_file
            preview_bgtempfile = self.bginfo.bg_file

        preview_bgmv = self.get_cached_bgvid(preview_bgtempfile, preview_profile, time_length)
        preview_affectmv = self.get_cached_effectvid(preview_affect, preview_profile, time_length)
        preview_bg_affect_mv = self.get_cached_bg_effect_file(preview_bgmv, preview_affectmv)

        preview_bg_aff_sub_mv = MvTempFile().getfullpath()
        self.ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                           preview_bg_affect_mv,
                                           preview_bg_aff_sub_mv)

        self.ffmpegcli.mux_audio_to_video(preview_bg_aff_sub_mv,
                                          self.songinfo.location,
                                          self.output
                                          )
        YtTempFile.delete_all()
        pass

    def get_cached_bg_effect_file(self, previewbgmv, previeweffectmv):
        cached_filename = Bg_Effect_CachedFile.get_cached_file_name(previewbgmv, previeweffectmv)
        effect_cachedfile = Bg_Effect_CachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = Bg_Effect_CachedFile.create_cachedfile(cached_filename)
            self.ffmpegcli.add_affect_to_video(previeweffectmv, previewbgmv, effect_cachedfile)
        return effect_cachedfile

    def get_cached_effect_file(self, preview_profile):
        cached_filename = EffectCachedFile.get_cached_profile_filename(self.effectinfo.effect_file,
                                                                       preview_profile)
        effect_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            self.ffmpegcli.scale_effect_vid(self.effectinfo.effect_file,
                                            preview_profile,
                                            effect_cachedfile)
        return effect_cachedfile

    def get_cached_backgroundimg(self, preview_profile):
        cached_filename = BgImgCachedFile.get_cached_profile_filename(self.bginfo.bg_file, preview_profile)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            self.ffmpegcli.scale_background_img(self.bginfo.bg_file,
                                                preview_profile,
                                                bg_cachedfile)
        return bg_cachedfile

    def get_cached_effectvid(self, preview_affect, preview_profile, time_length):
        cached_filename = EffectCachedFile.get_cached_profile_filename(preview_affect, preview_profile,
                                                                       extension='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            self.ffmpegcli.create_background_affect_with_length(preview_affect,
                                                                time_length,
                                                                preview_affectmv)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv

    def get_cached_bgvid(self, preview_bgtempfile, preview_profile, time_length):
        cached_filename = BgVidCachedFile.get_cached_profile_filename(preview_bgtempfile, preview_profile,
                                                                      extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            preview_bgmv = bgvid_cachedfile
            self.ffmpegcli.create_media_file_from_img(preview_bgtempfile, time_length, preview_bgmv)
        else:
            preview_bgmv = bgvid_cachedfile
        return preview_bgmv

    def build_preview(self):
        return self.build_mv(FFmpegProfile.PROFILE_MEDIUM.value)

    def build_release(self):
        return self.build_mv(FFmpegProfile.PROFILE_FULLHD.value)
