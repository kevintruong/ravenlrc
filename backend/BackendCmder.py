from enum import Enum

import json5

from backend.crawler.nct import *
from backend.crawler.subcrawler import *
from backend.render.ffmpegcli import FfmpegCli
from backend.subeffect.asseditor import *
from backend.subeffect.asseffect.LyricEffect import LyricEffect
from backend.subeffect.keyword.keyword import AssDialogueTextFormatter, AssDialueTextAnimatedTransform, \
    AssDialogueTextProcessor
from backend.utility.Utility import check_file_existed, FileInfo, generate_mv_filename

CurDir = os.path.dirname(os.path.realpath(__file__))
contentDir = os.path.join(CurDir, 'content')
cachedcontentdir = os.path.join(CurDir, 'content')


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
    CHANNELINFO_DIR = os.path.join(contentDir, 'ChannelInfo')

    @classmethod
    def get_file_path(cls, dir: str, filename: str):
        listfiles = os.listdir(dir)
        for file in listfiles:
            if filename in file:
                return os.path.join(dir, file)
        raise FileNotFoundError('Not found {} in {}'.format(filename, dir))


class CachedContentDir(Enum):
    SONG_DIR = os.path.join(cachedcontentdir, 'Song')
    EFFECT_DIR = os.path.join(cachedcontentdir, 'Effect')
    TITLE_DIR = os.path.join(cachedcontentdir, 'Title')
    MVCONF_DIR = os.path.join(cachedcontentdir, 'MvConfig')
    BGIMG_DIR = os.path.join(cachedcontentdir, 'BgImage')
    MVRELEASE_DIR = os.path.join(cachedcontentdir, 'Mv/Release')
    MVPREV_DIR = os.path.join(cachedcontentdir, 'Mv/Preview')
    FONTFILES_DIR = os.path.join(cachedcontentdir, 'Font')
    BUILDCMD_DIR = os.path.join(cachedcontentdir, 'BuildCmd')

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
    CachedEffectDir = os.path.join(CachedContentDir.EFFECT_DIR.value, '.cache')

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


class MuxAudioVidCachedFile(CachedFile):
    CachedEffectDir = os.path.join(CachedContentDir.BGIMG_DIR.value, '.cache')

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

    @classmethod
    def get_cached_file_name(cls, video, audio):
        videofilename = FileInfo(video).name
        videofilename = FileInfo(audio).name
        bgeff_cachedfilename = videofilename + '_' + videofilename + '.mp4'
        return bgeff_cachedfilename


class BgEffectCachedFile(CachedFile):
    CachedEffectDir = os.path.join(CachedContentDir.EFFECT_DIR.value, '.cache')
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
    def get_cached_file_name(cls, previewbgmv, previeweffectmv, opacity_val=0):
        bgmv_fileinfo = FileInfo(previewbgmv)
        effmv_fileinfo = FileInfo(previeweffectmv)
        bgeff_cachedfilename = bgmv_fileinfo.name + '_' + effmv_fileinfo.name + str(opacity_val) + '.mp4'
        return bgeff_cachedfilename


class BgImgCachedFile(CachedFile):
    CachedDir = os.path.join(CachedContentDir.BGIMG_DIR.value, '.cache')

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
    CachedBgVidDir = os.path.join(CachedContentDir.BGIMG_DIR.value, '.cache')

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
        # self.effect: BgEffect = None
        self.background: Background = None

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def run_create_single_background_mv(self):
        pass

    @abc.abstractmethod
    def run_create_multi_background_mv(self):
        pass

    @abc.abstractmethod
    def run_create_album_single_background(self):
        pass

    @abc.abstractmethod
    def run_create_album_multi_background(self):
        pass

    def get_cached_bg_effect_file(self, previewbgmv, previeweffectmv):
        ffmpegcli = FfmpegCli()
        cached_filename = BgEffectCachedFile.get_cached_file_name(previewbgmv, previeweffectmv,
                                                                  self.background.effect.opacity)
        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = BgEffectCachedFile.create_cachedfile(cached_filename)

            ffmpegcli.add_affect_to_video(previeweffectmv, previewbgmv, effect_cachedfile,
                                          self.background.effect.opacity)
        return effect_cachedfile

    def get_cached_effect_file(self, preview_profile):
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_profile_filename(self.background.effect.file,
                                                                       preview_profile)
        effect_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_effect_vid(self.background.effect.file,
                                       preview_profile,
                                       effect_cachedfile)
        return effect_cachedfile

    def get_cached_backgroundimg(self, preview_profile):
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_profile_filename(self.background.file, preview_profile)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_background_img(self.background.file,
                                           preview_profile,
                                           bg_cachedfile)
        return bg_cachedfile

    def get_cached_effectvid(self, preview_affect, preview_profile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_profile_filename(preview_affect, preview_profile,
                                                                       extension='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            ffmpegcli.create_background_affect_with_length(preview_affect,
                                                           time_length,
                                                           preview_affectmv)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv

    def get_cached_bgvid(self, preview_bgtempfile, preview_profile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = BgVidCachedFile.get_cached_profile_filename(preview_bgtempfile, preview_profile,
                                                                      extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            preview_bgmv = bgvid_cachedfile
            ffmpegcli.create_media_file_from_img(preview_bgtempfile, time_length, preview_bgmv)
        else:
            preview_bgmv = bgvid_cachedfile
        return preview_bgmv

    def get_cached_muxaudiovid(self, audiofile, videofile, time_length):
        cached_filename = MuxAudioVidCachedFile.get_cached_file_name(videofile, audiofile)

        effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effectmv_cachedfile = MuxAudioVidCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            ffmpegcli.mux_audio_to_video(videofile,
                                         audiofile,
                                         preview_affectmv,
                                         time_length)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv


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


class Position:
    def __init__(self, info: dict):
        self.x = info['x']
        self.y = info['y']


class Size:
    def __init__(self, info: dict):
        self.width = info['width']
        self.height = info['height']


class Font:
    def __init__(self, info: dict):
        self.name = info['name']
        self.color = info['color']
        self.size = info['size']


import json


class PyJSON(object):
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)

        self.from_dict(d)

    def from_dict(self, d):
        self.__dict__ = {}
        for key, value in d.items():
            if type(value) is dict:
                value = PyJSON(value)
            self.__dict__[key] = value

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if type(value) is PyJSON:
                value = value.to_dict()
            d[key] = value
        return d

    def __repr__(self):
        return str(self.to_dict())

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


class WordEffectConfigure:
    def __init__(self, configure):
        pass


class WordEffect(PyJSON):
    def __init__(self, d):
        """
        :self.code str
        :self.type str
        :param d:
        """
        super().__init__(d)
        # for keyvalue in effect.keys():
        #     if keyvalue == 'type':
        #         self.type = effect[keyvalue]
        #     if keyvalue == 'code':
        #         self.code = effect[keyvalue]
        #     if keyvalue == 'start':
        #         pass
        if 'config' in d:
            self.config = AssDialueTextAnimatedTransform(d['config'])


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
        self.opacity = info['opacity']
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


class BgTitle(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class BgWaterMask(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class Background:
    def __init__(self, info: dict):
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
                if keyvalue == 'configure':
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


class RenderCmder(Cmder):

    def run_create_album_multi_background(self):
        raise Exception("Not support render album multi background yet")
        pass

    def run_create_album_single_background(self):
        raise Exception("Not support render album single background yet")
        pass

    def run_create_multi_background_mv(self):
        raise Exception("Not support render  multi background MV yet")
        pass

    def run_create_single_background_mv(self):
        self.background = self.backgrounds[0]
        self.song_url = self.song_urls[0]
        self.song = SongInfo(self.songs[0])
        self.get_song_info_from_url()
        self.configure_output()
        try:
            if self.rendertype.type == RenderTypeCode.BUILD_PREVIEW.value:
                self.time_length = BuildCmder.preview_build_time_length
                self.build_preview()
            elif self.rendertype.type == RenderTypeCode.BUILD_RELEASE.value:
                self.build_release()
            return self.output
        except Exception as e:
            print("Exception as {}".format(e))
        pass

    def run(self):
        if self.kindVid == MusicVideoKind.MV_SINGLE_BACKGROUND:
            self.run_create_single_background_mv()
        elif self.kindVid == MusicVideoKind.MV_MULTI_BACKGROUND:
            return self.run_create_multi_background_mv()
        elif self.kindVid == MusicVideoKind.ALBUM_SINGLE_BACKGROUND:
            return self.run_create_album_single_background()
        elif self.kindVid == MusicVideoKind.ALBUM_MULTI_BACKGROUND:
            return self.run_create_album_multi_background()
        else:
            Exception("Not support render the Mv Kind {}".format(self.kindVid))
        pass

    def __init__(self, cmd: dict):
        super().__init__()
        self.rendertype = RenderType()
        self.song = None
        self.song_url = None
        self.output = None
        for keyvalue in cmd.keys():
            if keyvalue == 'song_urls':
                self.song_urls = cmd[keyvalue]
            if keyvalue == 'song':
                self.song = SongInfo(cmd[keyvalue])
            if keyvalue == 'songs':
                self.songs = cmd[keyvalue]
            if keyvalue == 'backgrounds':
                self.backgrounds = self.get_list_background(cmd[keyvalue])
            if keyvalue == 'spectrum':
                self.spectrum = Spectrum(cmd[keyvalue])
            if keyvalue == 'lyric':
                self.lyric = Lyric(cmd[keyvalue])
            if keyvalue == 'rendertype':
                self.rendertype = RenderType(cmd[keyvalue])
            if keyvalue == 'song_effect':
                self.song_effect = PyJSON(cmd[keyvalue])

        # self.get_song_info_from_url()
        # self.to_json()
        self.set_kind_of_video()

    def set_kind_of_video(self):
        num_songs = len(self.song_urls)
        num_backgrounds = len(self.backgrounds)
        if num_songs > 1 and num_backgrounds > 1:
            print('build album with multi background (album with multi background')
            self.kindVid = MusicVideoKind.ALBUM_MULTI_BACKGROUND
        if num_songs == 1 and num_backgrounds > 1:
            print('build MV with multi background (album with multi background')
            self.kindVid = MusicVideoKind.MV_MULTI_BACKGROUND
        if num_songs > 1 and num_backgrounds == 1:
            print('build album with single background (album with multi background')
            self.kindVid = MusicVideoKind.ALBUM_SINGLE_BACKGROUND
        if num_songs == 1 and num_backgrounds == 1:
            print('build a MV with single background ')
            self.kindVid = MusicVideoKind.MV_SINGLE_BACKGROUND
        else:
            self.kindVid = MusicVideoKind.MV_SINGLE_BACKGROUND

    def get_list_background(self, info: list):
        backgrounds = []
        for background_info in info:
            background = Background(background_info)
            backgrounds.append(background)
        return backgrounds

    def get_song_info_from_url(self):
        if self.song is None and self.song_url:
            crawlerdict = {
                'crawl_url': self.song_url,
                'output': ContentDir.SONG_DIR.value
            }
            crawler = CrawlCmder(crawlerdict)
            self.song: SongInfo = SongInfo(json.loads(crawler.run()))
            pass

    def configure_output(self):
        filename = generate_mv_filename(self.song.title)
        if self.rendertype.type == RenderTypeCode.BUILD_PREVIEW.value:
            self.output = os.path.join(ContentDir.MVPREV_DIR.value, filename)
        elif self.rendertype.type == RenderTypeCode.BUILD_RELEASE.value:
            self.output = os.path.join(ContentDir.MVRELEASE_DIR.value, filename)

    def to_json(self):
        buildfilename = FileInfo(self.output).name + '.json'
        buildfilepath = os.path.join(ContentDir.BUILDCMD_DIR.value, buildfilename)
        with open(buildfilepath, 'w') as file:
            json5.dump(self, file, default=lambda o: o.__dict__,
                       sort_keys=True, indent=4)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def build_mv(self, profile):
        preview_profile = profile
        ffmpegcli = FfmpegCli()

        ffmpegcli.set_resolution(preview_profile)
        preview_asstempfile = AssTempFile().getfullpath()

        create_ass_from_lrc(self.song.lyric,
                            preview_asstempfile,
                            self.background.lyric,
                            preview_profile)

        time_length = self.rendertype.configure.duration

        logger.debug(preview_profile)

        preview_asstempfile = self.apply_effect_lyric(preview_asstempfile)

        # if self.lyric.effect is not None:
        #     new_ass_effect = AssTempFile().getfullpath()
        #     preview_asstempfile
        # self.lyric.effect.apply_lyric_effect_to_file(preview_asstempfile, new_ass_effect)
        # preview_asstempfile = new_ass_effect
        # pass

        if self.background.effect is not None:
            if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
                preview_bgtempfile = self.get_cached_backgroundimg(preview_profile)
                preview_affect = self.get_cached_effect_file(preview_profile)
            else:
                preview_affect = self.background.effect.file
                preview_bgtempfile = self.background.file

            preview_bgmv = self.get_cached_bgvid(preview_bgtempfile, preview_profile, time_length)
            preview_affectmv = self.get_cached_effectvid(preview_affect, preview_profile, time_length)

            preview_bg_affect_mv = self.get_cached_bg_effect_file(preview_bgmv, preview_affectmv)

            audiovid_mv = self.get_cached_muxaudiovid(self.song.songfile, preview_bg_affect_mv, time_length)

            ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                          audiovid_mv,
                                          self.output)
        else:
            if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
                preview_bgtempfile = self.get_cached_backgroundimg(preview_profile)
            else:
                preview_bgtempfile = self.background.file

            preview_bgmv = self.get_cached_bgvid(preview_bgtempfile, preview_profile, time_length)

            audiovid_mv = self.get_cached_muxaudiovid(self.song.songfile, preview_bgmv, time_length)

            ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                          audiovid_mv,
                                          self.output)
            pass

        YtTempFile.delete_all()
        pass

    def build_preview(self):
        return self.build_mv(FFmpegProfile.PROFILE_MEDIUM.value)
        pass

    def build_release(self):

        pass

    def apply_effect_lyric(self, preview_asstempfile):
        new_ass_effect = AssTempFile().getfullpath()
        # preview_asstempfile
        # self.lyric.effect.apply_lyric_effect_to_file(preview_asstempfile, new_ass_effect)
        # preview_asstempfile = new_ass_effect
        try:
            for lyricword in self.lyric.words:
                if lyricword.effect:
                    lyricword.apply_lyric_effect_to_file(preview_asstempfile, preview_asstempfile)
                    print('process word data with the effect')
            return preview_asstempfile
        except Exception as e:
            print('error when process effect lyric,use the original effect file')
            return preview_asstempfile


class BuildCmder(Cmder):
    preview_build_time_length = 90

    def run(self):
        try:
            if self.build_type == BuildType.BUILD_PREVIEW:
                self.time_length = BuildCmder.preview_build_time_length
                self.build_preview()
            elif self.build_type == BuildType.BUILD_RELEASE:
                self.build_release()
            return self.output

        except Exception as e:
            print("Exception as {}".format(e))
            raise e

    def auto_reconfig_build_cmd(self):
        if self.build_type is None:
            self.build_type = BuildType.BUILD_RELEASE
        pass

    def toJSON(self):
        buildfilename = os.path.basename(self.configfile)
        buildfilepath = os.path.join(ContentDir.BUILDCMD_DIR.value, buildfilename)
        with open(buildfilepath, 'w') as file:
            json5.dump(self, file, default=lambda o: o.__dict__,
                       sort_keys=True, indent=4)

    def __init__(self, cmd: dict):
        super().__init__()
        try:
            self.song = None
            self.song_url = None
            self.build_type = None
            self.bginfo = None
            self.effect = None
            self.lyric_effect = None

            for field in cmd.keys():
                if 'type' in field:
                    self.build_type = BuildType(cmd[field])
                if 'song_url' in field:
                    self.song_url = cmd[field]
                if 'song' in field:
                    self.song = SongInfo()
                if 'background_info' in field:
                    self.bginfo = BackgroundInfo(cmd[field])
                if 'effect_info' in field:
                    self.effect = EffectInfo(cmd[field])
                if 'lyric_effect' in field:
                    self.lyric_effect = LyricEffect(cmd[field])
                if 'output' in field:
                    self.output = cmd[field]
                if 'configfile' in field:
                    self.configfile = cmd[field]
            self.get_song_info_from_url()
            self.auto_reconfig_build_cmd()

            ffmpegcli = FfmpegCli()
            self.time_length = ffmpegcli.get_media_time_length(self.song.songfile)
            self.configure_output()
            self.toJSON()
        except Exception as e:
            print("error {}".format(e))
            raise e

    def configure_output(self):
        filename = generate_mv_filename(self.song.title)
        if self.build_type == BuildType.BUILD_PREVIEW:
            self.output = os.path.join(ContentDir.MVPREV_DIR.value, filename)
        elif self.build_type == BuildType.BUILD_RELEASE:
            self.output = os.path.join(ContentDir.MVRELEASE_DIR.value, filename)

    def get_song_info_from_url(self):
        if self.song is None and self.song_url:
            crawlerdict = {
                'crawl_url': self.song_url,
                'output': ContentDir.SONG_DIR.value
            }
            crawler = CrawlCmder(crawlerdict)
            self.song: SongInfo = NctSongInfo(json.loads(crawler.run()))
            pass

    def build_mv(self, profile):
        preview_profile = profile
        ffmpegcli = FfmpegCli()

        ffmpegcli.set_resolution(preview_profile)
        preview_asstempfile = AssTempFile().getfullpath()

        create_ass_from_lrc(self.song.lyric,
                            preview_asstempfile,
                            self.bginfo.subinfo,
                            preview_profile)

        time_length = self.time_length

        logger.debug(preview_profile)

        if self.lyric_effect is not None:
            new_ass_effect = AssTempFile().getfullpath()
            # preview_asstempfile
            self.lyric_effect.apply_lyric_effect_to_file(preview_asstempfile, new_ass_effect)
            preview_asstempfile = new_ass_effect
            pass

        if self.effect is not None:
            if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
                preview_bgtempfile = self.get_cached_backgroundimg(preview_profile)
                preview_affect = self.get_cached_effect_file(preview_profile)
            else:
                preview_affect = self.effect.file
                preview_bgtempfile = self.bginfo.bg_file

            preview_bgmv = self.get_cached_bgvid(preview_bgtempfile, preview_profile, time_length)
            preview_affectmv = self.get_cached_effectvid(preview_affect, preview_profile, time_length)

            preview_bg_affect_mv = self.get_cached_bg_effect_file(preview_bgmv, preview_affectmv)

            preview_bg_aff_sub_mv = MvTempFile().getfullpath()
            ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                          preview_bg_affect_mv,
                                          preview_bg_aff_sub_mv)

            ffmpegcli.mux_audio_to_video(preview_bg_aff_sub_mv,
                                         self.song.songfile,
                                         self.output
                                         )
        else:
            if preview_profile != FFmpegProfile.PROFILE_FULLHD.value:
                preview_bgtempfile = self.get_cached_backgroundimg(preview_profile)
            else:
                preview_bgtempfile = self.bginfo.bg_file

            preview_bgmv = self.get_cached_bgvid(preview_bgtempfile, preview_profile, time_length)

            # preview_affectmv = self.get_cached_effectvid(preview_affect, preview_profile, time_length)

            preview_bg_affect_mv = preview_bgmv

            preview_bg_aff_sub_mv = MvTempFile().getfullpath()

            ffmpegcli.adding_sub_to_video(preview_asstempfile,
                                          preview_bg_affect_mv,
                                          preview_bg_aff_sub_mv)

            ffmpegcli.mux_audio_to_video(preview_bg_aff_sub_mv,
                                         self.song.songfile,
                                         self.output
                                         )
            pass

        YtTempFile.delete_all()
        pass

    def get_cached_bg_effect_file(self, previewbgmv, previeweffectmv):
        ffmpegcli = FfmpegCli()
        cached_filename = BgEffectCachedFile.get_cached_file_name(previewbgmv, previeweffectmv, self.effect.opacity)
        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = BgEffectCachedFile.create_cachedfile(cached_filename)

            ffmpegcli.add_affect_to_video(previeweffectmv, previewbgmv, effect_cachedfile, self.effect.opacity)
        return effect_cachedfile

    def get_cached_effect_file(self, preview_profile):
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_profile_filename(self.effect.file,
                                                                       preview_profile)
        effect_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_effect_vid(self.effect.file,
                                       preview_profile,
                                       effect_cachedfile)
        return effect_cachedfile

    def get_cached_backgroundimg(self, preview_profile):
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_profile_filename(self.bginfo.bg_file, preview_profile)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_background_img(self.bginfo.bg_file,
                                           preview_profile,
                                           bg_cachedfile)
        return bg_cachedfile

    def get_cached_effectvid(self, preview_affect, preview_profile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_profile_filename(preview_affect, preview_profile,
                                                                       extension='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            ffmpegcli.create_background_affect_with_length(preview_affect,
                                                           time_length,
                                                           preview_affectmv)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv

    def get_cached_bgvid(self, preview_bgtempfile, preview_profile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = BgVidCachedFile.get_cached_profile_filename(preview_bgtempfile, preview_profile,
                                                                      extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            preview_bgmv = bgvid_cachedfile
            ffmpegcli.create_media_file_from_img(preview_bgtempfile, time_length, preview_bgmv)
        else:
            preview_bgmv = bgvid_cachedfile
        return preview_bgmv

    def build_preview(self):
        return self.build_mv(FFmpegProfile.PROFILE_MEDIUM.value)

    def build_release(self):
        return self.build_mv(FFmpegProfile.PROFILE_FULLHD.value)
