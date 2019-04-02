from abc import *
from threading import Thread

from backend.render.cache import *
from backend.render.type import *
from backend.utility.TempFileMnger import *

from backend.render.parser import SongApi
from backend.crawler.nct import SongInfo
from backend.render.ffmpegcli import FfmpegCli, FFmpegProfile
from backend.subeffect.asseditor import create_ass_from_lrc
from backend.utility.Utility import generate_mv_filename
from backend.yclogger import telelog


class RenderEngine(ABC):
    def __init__(self, rendertype=None):
        if rendertype is None:
            self.rendertype = rendertype
        else:
            self.rendertype = RenderType()
        pass

    @abstractmethod
    def run(self, src: str, **kwargs):
        pass


class RenderSong(RenderEngine):

    def run(self, src: str, **kwargs):
        cached_filename, effectmv_cachedfile = self.get_cached_file(src)
        if effectmv_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effectmv_cachedfile = MuxAudioVidCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.mux_audio_to_video(src,
                                         self.songinfo.songfile,
                                         effectmv_cachedfile)
            CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
        return effectmv_cachedfile

    def get_cached_file(self, src):
        cached_filename = MuxAudioVidCachedFile.get_cached_file_name(src, self.songinfo.songfile)
        effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        return cached_filename, effectmv_cachedfile

    def __init__(self, songinfo: SongInfo):
        super().__init__()
        self.songinfo = songinfo


class RenderSpectrum(RenderEngine):
    def __init__(self, spectrumconf: BgSpectrum, spectrum: Spectrum, rendertype: RenderType):
        super().__init__(rendertype)
        self.spectrumconf = spectrumconf
        self.spectrum = spectrum

    def format(self):
        timelength = self.rendertype.configure.duration
        src = self.spectrum.file
        renderfile_name = CachedFile.get_cached_filename(src,
                                                         attribute=self.spectrumconf)

        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if renderfile is None:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            # formatted_spectrum = SpectrumMvTemplateFile().getfullpath()
            ffmpegcli = FfmpegCli()
            ffmpegcli.scale_video_by_width_height(self.spectrum.file,
                                                  self.spectrumconf.size,
                                                  renderfile,
                                                  timelength=timelength)
            CachedContentDir.gdrive_file_upload(renderfile)
        return renderfile

    def run(self, src: str, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src,
                                                              self.spectrum.file,
                                                              self.spectrumconf.size)
        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not renderfile:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formatted_watermask = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formatted_watermask, renderfile, self.spectrumconf.position)
            CachedContentDir.gdrive_file_upload(renderfile)
        return renderfile


class RenderWaterMask(RenderEngine):
    def __init__(self, watermaskconf: BgWaterMask,
                 watermask: WaterMask, rendertype=None):
        super().__init__(rendertype)
        self.watermaskconf = watermaskconf
        self.watermask = watermask

    def format(self):
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_video_by_width_height(self.watermask.file, self.watermaskconf.size, formatted_watermask)
        return formatted_watermask
        pass

    def run(self, src: str, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src, self.watermask.file, self.watermaskconf.size)
        output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not output:
            output = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formatted_watermask = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formatted_watermask, output, self.watermaskconf.position)
            CachedContentDir.gdrive_file_upload(output)
        return output


class RenderTitle(RenderEngine):
    def __init__(self, titleconf: BgTitle, title: Title, rendertype=None):
        super().__init__(rendertype)
        self.titleconf = titleconf
        self.title = title

    def format(self):
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_video_by_width_height(self.title.file, self.titleconf.size, formatted_watermask)
        return formatted_watermask

    def run(self, src: str, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src, self.title.file, self.titleconf.size)
        output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not output:
            output = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formattedtitle_img = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formattedtitle_img, output, self.titleconf.position)
            CachedContentDir.gdrive_file_upload(output)
        return output


class RenderBgEffect(RenderEngine):

    def run(self, src: str, **kwargs):
        profile = self.rendertype.configure.resolution
        timelength = self.rendertype.configure.duration
        cached_filename, output, effect_file = self.get_effect_cached_file(profile,
                                                                           src,
                                                                           timelength)

        if output is None:
            ffmpegcli = FfmpegCli()
            output = BgEffectCachedFile.create_cachedfile(cached_filename)

            ffmpegcli.add_affect_to_video(effect_file,
                                          src,
                                          output,
                                          self.bgEffect.opacity)
            CachedContentDir.gdrive_file_upload(output)
        return output

    def get_effect_cached_file(self, profile, src, timelength):
        self.bgeffectfile = self.init_bgeffect_by_profile(profile)
        effect_file = self.init_bgeffect_video_with_length(self.bgeffectfile, timelength)
        cached_filename = BgEffectCachedFile.get_cached_file_name(src, effect_file,
                                                                  self.bgEffect.opacity)
        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        return cached_filename, effect_cachedfile, effect_file

    def __init__(self, bgeffect: BgEffect, rendertype=None):
        super().__init__(rendertype)
        self.bgEffect = bgeffect
        self.bgeffectfile = None

    def init_bgeffect_by_profile(self, profile):
        '''
        create background effect video scaled by profile
        :param profile:
        :return:
        '''
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_filename(self.bgEffect.file,
                                                               attribute=profile)
        effect_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_effect_vid(self.bgEffect.file,
                                       self.rendertype.configure.resolution,
                                       effect_cachedfile)
            CachedContentDir.gdrive_file_upload(effect_cachedfile)
        return effect_cachedfile

    def init_bgeffect_video_with_length(self, effectprofilefile, length):
        '''
        loop the current file effect_profile_file with time length is length
        :param effectprofilefile:
        :param length:
        :return:
        '''
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_filename(effectprofilefile,
                                                               extention='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            ffmpegcli.create_background_affect_with_length(effectprofilefile,
                                                           length,
                                                           preview_affectmv)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv
        pass


class RenderLyric(RenderEngine):
    reference_resolution_width = 1920
    reference_resolution_height = 1080

    def __init__(self,
                 lrcconf: BgLyric,
                 lyric: Lyric,
                 lyricfile=None,
                 rendertype=None):
        super().__init__(rendertype)
        self.lyric = lyric
        self.lrcconf = lrcconf

        if self.lyric is None:
            self.lyricfile = lyricfile
        else:
            if self.lyric.file:
                self.lyricfile = self.lyric.file
            else:
                self.lyricfile = lyricfile
        self.assfile = self.generate_lyric_effect_file()

    def generate_lyric_effect_file(self):
        resolution = self.rendertype.configure.resolution
        scale_factor = self.rendertype.configure.resolution.width / self.reference_resolution_width
        self.lrcconf.scale_font_size_by_factor(scale_factor)
        cached_filename = LyricCachedFile.get_cached_filename(self.lyricfile, attribute=self, extension='.ass')
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        if cachedfilepath is None:
            cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
            create_ass_from_lrc(self.lyricfile,
                                cachedfilepath,
                                self.lrcconf,
                                resolution)
            cachedfilepath = self.create_effect_lyric_file(cachedfilepath)
            CachedContentDir.gdrive_file_upload(cachedfilepath)
        return cachedfilepath

    def run(self, src: str, **kwargs):
        if 'output' in kwargs:
            output = kwargs['output']

        cached_filename = LyricCachedFile.get_cached_filename(src, attribute=self.assfile)
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        if cachedfilepath is None:
            cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            ffmpegcli.adding_sub_to_video(self.assfile,
                                          src,
                                          cachedfilepath)
            CachedContentDir.gdrive_file_upload(cachedfilepath)
        return cachedfilepath

    def create_effect_lyric_file(self, ass_file):
        try:
            if self.lyric:
                for lyricword in self.lyric.words:
                    if lyricword.effect:
                        ass_file = lyricword.apply_lyric_effect_to_file(ass_file)
                return ass_file
        except Exception as exp:
            print('error when process effect lyric,use the original effect file')
            return ass_file
        return ass_file


class BackgroundRender(RenderEngine):

    def get_cached_backgroundimg(self):
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_filename(self.input,
                                                              attribute=self.rendertype.configure.resolution)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_img_by_width_height(self.input,
                                                self.rendertype.configure.resolution,
                                                bg_cachedfile)
        return bg_cachedfile

    def get_cached_bgvid(self, bgfile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = BgVidCachedFile.get_cached_filename(bgfile,
                                                              attribute=self.rendertype.configure,
                                                              extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            preview_bgmv = bgvid_cachedfile
            ffmpegcli.create_media_file_from_img(input_img=bgfile,
                                                 time_length=time_length,
                                                 output_video=preview_bgmv)
        else:
            preview_bgmv = bgvid_cachedfile
        return preview_bgmv

    def render_background_based_timming(self):
        print('not support yet')

    def render_background_full_time_length(self):
        timeleng = self.rendertype.configure.duration
        self.input = self.file  # initial input by background file
        if self.watermask:
            telelog.debug("render watermask")
            self.output = self.watermask.run(self.input)
            self.input = self.output
        if self.title:
            telelog.debug("render title")
            self.output = self.title.run(self.input)
            self.input = self.output
        if self.file:
            telelog.debug("render background file")
            self.input = self.get_cached_backgroundimg()
            self.output = self.get_cached_bgvid(self.input, timeleng)
            self.input = self.output
        if self.effect:
            telelog.debug("render effect file")
            self.output = self.effect.run(self.input)
            self.input = self.output
        if self.spectrum:
            telelog.debug("render spectrum file")
            self.output = self.spectrum.run(self.input)
            self.input = self.output
        if self.song:
            telelog.debug("render song file {}".format("hello world"))
            self.output = self.song.run(self.input)
            self.input = self.output
        if self.lyric:
            telelog.critical("render lyric file")
            self.output = self.lyric.run(self.input, output=self.finalfile)
        output_url = ContentDir.gdrive_file_upload(self.output)
        return output_url

    def init_background_render(self):
        return self.get_cached_backgroundimg()

    def run(self, src: str, **kwargs):
        self.detect_rendertype()
        # if self.timming:
        #     TODO need to implement for the new feature
        # pass
        # else:
        return self.render_background_full_time_length()
        pass

    def __init__(self):
        super().__init__()
        self.profile = None
        self.song: RenderSong = None
        self.file: str = None
        self.timming: list = None
        self.effect: RenderBgEffect = None
        self.title: RenderTitle = None
        self.watermask: RenderWaterMask = None
        self.lyric: RenderLyric = None
        self.spectrum: RenderSpectrum = None
        self.rendertype: RenderType = None
        self.input = None
        self.output = None
        self.finalfile = None

    def detect_rendertype(self):
        filename = generate_mv_filename(self.song.songinfo.title)
        if self.rendertype:
            if self.rendertype.type == RenderTypeCode.BUILD_PREVIEW.value:
                self.finalfile = os.path.join(ContentDir.MVPREV_DIR, filename)
                self.profile = FFmpegProfile.PROFILE_MEDIUM.value
            else:
                self.profile = FFmpegProfile.PROFILE_FULLHD
                self.output = os.path.join(ContentDir.MVRELEASE_DIR, filename)
        else:
            self.profile = FFmpegProfile.PROFILE_MEDIUM.value


class BackgroundsRender:

    def run(self):
        bgrender_engine: BackgroundRender
        for bgrender_engine in self.bgrenderengine:
            # TODO for now return for the first background render
            url_ret = bgrender_engine.run(bgrender_engine.input)
            telelog.critical("url return {}".format(url_ret))
            pass
        pass
        return url_ret

    def generate_render_engine(self):
        for index, background_item in enumerate(self.songapi.backgrounds):
            bgRender = BackgroundRender()
            if self.songapi.rendertype:
                bgRender.rendertype = self.songapi.rendertype
            if background_item.file:
                bgRender.file = background_item.file
            if background_item.effect:
                bgRender.effect = RenderBgEffect(background_item.effect,
                                                 bgRender.rendertype)
            if background_item.title and self.songapi.title:
                bgRender.title = RenderTitle(background_item.title,
                                             self.songapi.title,
                                             bgRender.rendertype)
            if background_item.lyric:
                lyricfile = self.songapi.song.lyric
                bgRender.lyric = RenderLyric(background_item.lyric,
                                             self.songapi.lyric,
                                             lyricfile,
                                             bgRender.rendertype)
            if background_item.spectrum and self.songapi.spectrum:
                bgRender.spectrum = RenderSpectrum(background_item.spectrum,
                                                   self.songapi.spectrum,
                                                   bgRender.rendertype)
            if background_item.watermask and self.songapi.watermask:
                bgRender.watermask = RenderWaterMask(background_item.watermask,
                                                     self.songapi.watermask,
                                                     bgRender.rendertype)
            if self.songapi.song:
                bgRender.song = RenderSong(self.songapi.song)
            if background_item.timing:
                print('not support yet')

            self.bgrenderengine.append(bgRender)
            pass

    def __init__(self, renderdata: SongApi):
        self.bgrenderengine = []
        self.songapi = renderdata
        self.generate_render_engine()
        super().__init__()


import unittest
import os
import json


class Test_Render_Engine(unittest.TestCase):
    def setUp(self):
        jsonfile = r'/mnt/Data/Project/ytcreatorservice/test/request.json'
        with open(jsonfile, 'r', encoding='UTF-8') as json5file:
            self.data = json.load(json5file)
        jsondata = json.dumps(self.data, indent=1)
        telelog.debug(jsondata)
        self.renderconf = SongApi(self.data)
        log = self.renderconf.toJSON()
        print(log)
        self.bgsRender = BackgroundsRender(self.renderconf)

    def test_run(self):
        output = self.bgsRender.run()
        print(output)
        pass
