from abc import *

from backend.BackendCmder import SongApi, WaterMask, RenderTypeCode, BgTitle
from backend.crawler.nct import SongInfo
from backend.render.cache import ContentDir, EffectCachedFile, SecondBgImgCachedFile, MuxAudioVidCachedFile, \
    BgEffectCachedFile, BgImgCachedFile, BgVidCachedFile
from backend.render.ffmpegcli import FfmpegCli, FFmpegProfile
from backend.render.type import Lyric, Spectrum, BgSpectrum, BgEffect, BgWaterMask, BgLyric, Title, RenderType
from backend.subeffect.asseditor import create_ass_from_lrc
from backend.utility.TempFileMnger import AssTempFile, PngTempFile, SpectrumMvTemplateFile
from backend.utility.Utility import generate_mv_filename


class RenderEngine(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, src: str, profile, timelength, **kwargs):
        pass


class RenderSong(RenderEngine):

    def run(self, src: str, profile, timelength, **kwargs):
        cached_filename = MuxAudioVidCachedFile.get_cached_file_name(src, self.songinfo.songfile)
        effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effectmv_cachedfile = MuxAudioVidCachedFile.create_cachedfile(cached_filename)
            preview_affectmv = effectmv_cachedfile
            ffmpegcli.mux_audio_to_video(src,
                                         self.songinfo.songfile,
                                         preview_affectmv,
                                         timelength)
        else:
            preview_affectmv = effectmv_cachedfile
        return preview_affectmv
        pass

    def __init__(self, songinfo: SongInfo):
        super().__init__()
        self.songinfo = songinfo


class RenderSpectrum(RenderEngine):
    def __init__(self, spectrumconf: BgSpectrum, spectrum: Spectrum):
        super().__init__()
        self.spectrumconf = spectrumconf
        self.spectrum = spectrum

    def format(self):
        formatted_watermask = SpectrumMvTemplateFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_media_by_width_ratio(self.spectrum.file, self.spectrumconf.size, formatted_watermask)
        return formatted_watermask
        pass

    def run(self, src: str, profile, timelength, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src, self.spectrum.file, self.spectrumconf.size)
        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not renderfile:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formatted_watermask = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formatted_watermask, renderfile, self.spectrumconf.position)
        return renderfile

        return src
        pass


class RenderWaterMask(RenderEngine):
    def __init__(self, watermaskconf: BgWaterMask, watermask: WaterMask):
        super().__init__()
        self.watermaskconf = watermaskconf
        self.watermask = watermask

    def format(self):
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_media_by_width_ratio(self.watermask.file, self.watermaskconf.size, formatted_watermask)
        return formatted_watermask
        pass

    def run(self, src: str, profile, timelength, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src, self.watermask.file, self.watermaskconf.size)
        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not renderfile:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formatted_watermask = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formatted_watermask, renderfile, self.watermaskconf.position)
        return renderfile


class RenderTitle(RenderEngine):
    def __init__(self, titleconf: BgTitle, title: Title):
        super().__init__()
        self.titleconf = titleconf
        self.title = title

    def format(self):
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_media_by_width_ratio(self.title.file, self.titleconf.size, formatted_watermask)
        return formatted_watermask

    def run(self, src: str, profile, timelength, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src, self.title.file, self.titleconf.size)
        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not renderfile:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formattedtitle_img = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formattedtitle_img, renderfile, self.titleconf.position)
        return renderfile


class RenderBgEffect(RenderEngine):
    def run(self, src: str, profile, timelength, **kwargs):
        self.bgeffectfile = self.init_bgeffect_by_profile(profile)
        effect_file = self.init_bgeffect_video_with_length(self.bgeffectfile, timelength)
        ffmpegcli = FfmpegCli()

        cached_filename = BgEffectCachedFile.get_cached_file_name(src, effect_file,
                                                                  self.bgEffect.opacity)
        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = BgEffectCachedFile.create_cachedfile(cached_filename)

            ffmpegcli.add_affect_to_video(effect_file, src, effect_cachedfile,
                                          self.bgEffect.opacity)
        return effect_cachedfile

    def __init__(self, bgeffect: BgEffect):
        super().__init__()
        self.bgEffect = bgeffect
        self.bgeffectfile = None

    def init_bgeffect_by_profile(self, profile):
        '''
        create background effect video scaled by profile
        :param profile:
        :return:
        '''
        ffmpegcli = FfmpegCli()
        ffmpegcli.set_resolution(profile)
        cached_filename = EffectCachedFile.get_cached_profile_filename(self.bgEffect.file,
                                                                       profile)
        effect_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_effect_vid(self.bgEffect.file,
                                       profile,
                                       effect_cachedfile)
        return effect_cachedfile

    def init_bgeffect_video_with_length(self, effectprofilefile, length):
        '''
        loop the current file effect_profile_file with time length is length
        :param effectprofilefile:
        :param length:
        :return:
        '''
        ffmpegcli = FfmpegCli()
        cached_filename = EffectCachedFile.get_cached_profile_filename(effectprofilefile,
                                                                       extension='.mp4')
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

    def __init__(self, lrcconf: BgLyric, lyric: Lyric):
        super().__init__()
        self.lyric = lyric
        self.lrcconf = lrcconf

    def generate_lyric_effect_file(self, preview_profile):
        preview_asstempfile = AssTempFile().getfullpath()
        create_ass_from_lrc(self.lyric.file,
                            preview_asstempfile,
                            self.lrcconf,
                            preview_profile)
        preview_asstempfile = self.create_effect_lyric_file(preview_asstempfile)
        return preview_asstempfile

    def run(self, src: str, profile, timelength, **kwargs):
        if 'output' in kwargs:
            output = kwargs['output']
        ffmpegcli = FfmpegCli()
        ffmpegcli.set_resolution(profile)
        assfile = self.generate_lyric_effect_file(profile)
        ffmpegcli.adding_sub_to_video(assfile,
                                      src,
                                      output)
        return output

    def create_effect_lyric_file(self, ass_file):
        try:
            for lyricword in self.lyric.words:
                if lyricword.effect:
                    ass_file = lyricword.apply_lyric_effect_to_file(ass_file)
            return ass_file
        except Exception as exp:
            print('error when process effect lyric,use the original effect file')
            return ass_file


class BackgroundRender:

    def get_cached_backgroundimg(self, preview_profile):
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_profile_filename(self.input, preview_profile)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_background_img(self.input,
                                           preview_profile,
                                           bg_cachedfile)
        return bg_cachedfile

    def get_cached_bgvid(self, bgfile, time_length):
        ffmpegcli = FfmpegCli()
        cached_filename = BgVidCachedFile.get_cached_profile_filename(bgfile,
                                                                      extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            preview_bgmv = bgvid_cachedfile
            ffmpegcli.create_media_file_from_img(bgfile, time_length, preview_bgmv)
        else:
            preview_bgmv = bgvid_cachedfile
        return preview_bgmv

    def render_background_based_timming(self):
        print('not support yet')

    def render_background_full_time_length(self):
        timeleng = self.rendertype.configure.duration
        self.input = self.file
        if self.watermask:
            self.output = self.watermask.run(self.input, self.profile, timeleng)
            self.input = self.output
        if self.title:
            self.output = self.title.run(self.input, self.profile, timeleng)
            self.input = self.output
        self.get_cached_backgroundimg(self.profile)
        self.output = self.get_cached_bgvid(self.input, timeleng)
        self.input = self.output
        if self.effect:
            self.output = self.effect.run(self.input, self.profile, timeleng)
            self.input = self.output
        if self.spectrum:
            self.output = self.spectrum.run(self.input, self.profile, timeleng)
            self.input = self.output
        if self.song:
            self.output = self.song.run(self.input, self.profile, timeleng)
            self.input = self.output
        if self.lyric:
            self.output = self.lyric.run(self.input, self.profile, timeleng, output=self.finalfile)
        return self.output

    def init_background_render(self):
        return self.get_cached_backgroundimg(self.profile)

    def run(self):
        self.detect_rendertype()
        # self.input = self.init_background_render()
        if self.timming:
            pass
        else:
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
                self.finalfile = os.path.join(ContentDir.MVPREV_DIR.value, filename)
                self.profile = FFmpegProfile.PROFILE_MEDIUM.value
            else:
                self.profile = FFmpegProfile.PROFILE_FULLHD.value
                self.output = os.path.join(ContentDir.MVRELEASE_DIR.value, filename)
        else:
            self.profile = FFmpegProfile.PROFILE_MEDIUM.value


class BackgroundsRender:
    def run(self):
        bgrender_engine: BackgroundRender
        for bgrender_engine in self.bgrenderengine:
            bgrender_engine.run()
            pass
        pass

    def generate_render_engine(self):
        for index, background_item in enumerate(self.renderinfo.backgrounds):
            bgRender = BackgroundRender()
            if background_item.file:
                bgRender.file = background_item.file
            if background_item.effect:
                bgRender.effect = RenderBgEffect(background_item.effect)
            if background_item.title and self.renderinfo.title:
                bgRender.title = RenderTitle(background_item.title, self.renderinfo.title)
            if background_item.lyric and self.renderinfo.lyric:
                if self.renderinfo.song:
                    self.renderinfo.lyric.file = self.renderinfo.song.lyric
                bgRender.lyric = RenderLyric(background_item.lyric, self.renderinfo.lyric)
            if background_item.spectrum and self.renderinfo.spectrum:
                bgRender.spectrum = RenderSpectrum(background_item.spectrum,
                                                   self.renderinfo.spectrum)
            if background_item.watermask and self.renderinfo.watermask:
                bgRender.watermask = RenderWaterMask(background_item.watermask,
                                                     self.renderinfo.watermask)
            if self.renderinfo.song:
                bgRender.song = RenderSong(self.renderinfo.song)
            if background_item.timing:
                print('not support yet')
            if self.renderinfo.rendertype:
                bgRender.rendertype = self.renderinfo.rendertype
            self.bgrenderengine.append(bgRender)
            pass

    def __init__(self, renderdata: SongApi):
        self.bgrenderengine = []
        self.renderinfo = renderdata
        self.generate_render_engine()
        super().__init__()


import unittest
import os
import json


class Test_Render_Engine(unittest.TestCase):
    def setUp(self):
        jsonfile = r'D:\Project\ytcreatorservice\test\request.json'
        with open(jsonfile, 'r', encoding='UTF-8') as json5file:
            self.data = json.load(json5file)
        self.renderconf = SongApi(self.data)
        self.bgsRender = BackgroundsRender(self.renderconf)

    def test_run(self):
        output = self.bgsRender.run()
        print(output)
        pass
