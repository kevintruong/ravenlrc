from abc import *

from Api.songeffect import generate_songeffect_for_lrc
from backend.type import SongInfo
from backend.utility.TempFileMnger import *
from backend.utility.Utility import generate_mv_filename
from backend.yclogger import telelog
from render.cache import *
from render.ffmpegcli import FfmpegCli, FFmpegProfile
from render.parser import SongApi
from render.type import *


# from subeffect.asseditor import create_ass_from_lrc
# from crawler.nct import SongInfo


class RenderEngine(ABC):
    def __init__(self, rendertype=None):
        if rendertype is None:
            self.rendertype = RenderType()
        else:
            self.rendertype = rendertype
        pass

    @abstractmethod
    def run(self, src: str, **kwargs):
        pass


class RenderSong(RenderEngine):

    def run(self, src: ContentFileInfo, **kwargs):
        cached_filename = CachedFile.get_cached_filename(src.filename,
                                                         attribute=[self.rendertype,
                                                                    self.songinfo])
        effectmv_cachedfile = self.get_cached_file(cached_filename)
        if effectmv_cachedfile is None:
            self.songinfo.songfile = GDriveMnger(True).download_file(self.songinfo.songfile)
            src = src.get()
            ffmpegcli = FfmpegCli()
            effectmv_cachedfile = MuxAudioVidCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.mux_audio_to_video(src,
                                         self.songinfo.songfile,
                                         effectmv_cachedfile)
            CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
            effectmv_cachedfile = self.get_cached_file(cached_filename)
        return effectmv_cachedfile

    def get_cached_file(self, cached_filename):
        effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        return effectmv_cachedfile

    def __init__(self, songinfo: SongInfo):
        super().__init__()
        self.songinfo = songinfo


class RenderSpectrum(RenderEngine):
    def __init__(self, spectrumconf: BgSpectrum, rendertype: RenderType):
        super().__init__(rendertype)
        self.spectrumconf = spectrumconf
        self.formatted_watermask = None

    def format(self):
        timelength = self.rendertype.configure.duration
        src = self.spectrumconf.file.filename
        renderfile_name = CachedFile.get_cached_filename(src,
                                                         attribute=[self.rendertype,
                                                                    self.spectrumconf.custom,
                                                                    self.spectrumconf.templatecode])

        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if renderfile is None:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            ffmpegcli = FfmpegCli()
            ffmpegcli.scale_video_by_width_height(self.spectrumconf.file.get(),
                                                  self.spectrumconf.size,
                                                  renderfile,
                                                  timelength=timelength)
            CachedContentDir.gdrive_file_upload(renderfile)
        return renderfile

    def run(self, src: str, **kwargs):
        self.formatted_watermask = self.format()
        renderfile_name = CachedFile.get_cached_filename(src, attribute=[self.rendertype,
                                                                         self.formatted_watermask,
                                                                         self.spectrumconf.custom,
                                                                         self.spectrumconf.templatecode])
        renderfile = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not renderfile:
            renderfile = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src,
                                         self.formatted_watermask,
                                         renderfile,
                                         self.spectrumconf.position)
            CachedContentDir.gdrive_file_upload(renderfile)
        return renderfile


class RenderWaterMask(RenderEngine):
    def __init__(self, watermaskconf: BgWaterMask,
                 rendertype=None):
        super().__init__(rendertype)
        self.watermaskconf = watermaskconf

    def format(self):
        self.watermaskconf.file = self.watermaskconf.file.get()
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_video_by_width_height(self.watermaskconf.file,
                                              self.watermaskconf.size,
                                              formatted_watermask)
        return formatted_watermask
        pass

    def run(self, src, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src,
                                                              self.watermaskconf.file.filename,
                                                              self.watermaskconf.size)
        output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not output:
            src: ContentFileInfo
            src = src.get()
            output = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formatted_watermask = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src,
                                         formatted_watermask,
                                         output,
                                         self.watermaskconf.position)
            CachedContentDir.gdrive_file_upload(output)
        return output


class RenderTitle(RenderEngine):
    def __init__(self, titleconf: BgTitle, rendertype=None):
        super().__init__(rendertype)
        self.titleconf = titleconf
        # self.title = title

    def format(self):
        formatted_watermask = PngTempFile().getfullpath()
        ffmpegcli = FfmpegCli()
        ffmpegcli.scale_video_by_width_height(self.titleconf.file.get(),
                                              self.titleconf.size,
                                              formatted_watermask)
        return formatted_watermask

    def run(self, src, **kwargs):
        src: ContentFileInfo
        renderfile_name = SecondBgImgCachedFile.get_file_name(src,
                                                              self.titleconf.file.filename,
                                                              self.titleconf.size)
        output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not output:
            output = SecondBgImgCachedFile.create_cachedfile(renderfile_name)
            formattedtitle_img = self.format()
            ffmpegcli = FfmpegCli()
            ffmpegcli.add_logo_to_bg_img(src, formattedtitle_img, output, self.titleconf.position)
            CachedContentDir.gdrive_file_upload(output)
        return output


class RenderBgEffect(RenderEngine):

    def run(self, src: ContentFileInfo, **kwargs):
        profile = self.rendertype.configure.resolution
        timelength = self.rendertype.configure.duration

        self.bgeffectfile = self.init_bgeffect_by_profile(profile)

        effect_file = self.init_bgeffect_video_with_length(self.bgeffectfile,
                                                           timelength)

        cached_filename = BgEffectCachedFile.get_cached_filename(src.filename,
                                                                 attribute=[effect_file.filename,
                                                                            self.bgEffect.opacity])

        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)

        # cached_filename, output, effect_file = self.get_effect_cached_file(profile,
        #                                                                    src,
        #                                                                    timelength)

        if effect_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effect_cachedfile = BgEffectCachedFile.create_cachedfile(cached_filename)
            effect_file = effect_file.get()
            src = src.get()
            ffmpegcli.add_affect_to_video(effect_file,
                                          src,
                                          effect_cachedfile,
                                          self.bgEffect.opacity)
            CachedContentDir.gdrive_file_upload(effect_cachedfile)
            effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        return effect_cachedfile

    def get_effect_cached_file(self, profile, src: ContentFileInfo, timelength):
        self.bgeffectfile = self.init_bgeffect_by_profile(profile)

        effect_file = self.init_bgeffect_video_with_length(self.bgeffectfile,
                                                           timelength)

        cached_filename = BgEffectCachedFile.get_cached_filename(src.filename,
                                                                 attribute=[effect_file.filename,
                                                                            self.bgEffect.opacity])

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
        # self.bgEffect.file = self.bgEffect.file.get()
        cached_filename = EffectCachedFile.get_cached_filename(self.bgEffect.file.filename,
                                                               attribute=profile)
        effect_cachedfile: ContentFileInfo = EffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            ffmpegcli = FfmpegCli()
            self.bgEffect.file = self.bgEffect.file.get()
            effect_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.scale_effect_vid(self.bgEffect.file,
                                       self.rendertype.configure.resolution,
                                       effect_cachedfile)
            CachedContentDir.gdrive_file_upload(effect_cachedfile)
            effect_cachedfile: ContentFileInfo = EffectCachedFile.get_cachedfile(cached_filename)
        return effect_cachedfile

    def init_bgeffect_video_with_length(self, effectprofilefile, length):
        '''
        loop the current file effect_profile_file with time length is length
        :param effectprofilefile:
        :param length:
        :return:
        '''
        cached_filename = EffectCachedFile.get_cached_filename(effectprofilefile.filename,
                                                               attribute=self.rendertype,
                                                               extention='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effectprofilefile = effectprofilefile.get()
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.create_background_affect_with_length(effectprofilefile,
                                                           length,
                                                           effectmv_cachedfile)
            # CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
            effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        return effectmv_cachedfile


class RenderLyric(RenderEngine):
    reference_resolution_width = 1920
    reference_resolution_height = 1080

    def __init__(self,
                 lrcconf: BgLyric,
                 lyric: Lyric,
                 lyricfile=None,
                 songeffect=None,
                 rendertype=None):
        super().__init__(rendertype)
        self.lyric = lyric
        self.lrcconf = lrcconf
        self.lyricfile = lyricfile
        if songeffect:
            self.songeffect = songeffect
        self.assfile = self.generate_lyric_effect_file()

    def generate_lyric_effect_file(self):
        scale_factor = self.rendertype.configure.resolution.width / self.reference_resolution_width
        self.lrcconf.scale_font_size_by_factor(scale_factor)
        cached_filename = LyricCachedFile.get_cached_filename(self.lyricfile,
                                                              attribute=self,
                                                              extension='.ass')
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        if cachedfilepath is None:
            cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
            if self.songeffect:
                # create_ass_from_lrc(self.lyricfile,
                #                     cachedfilepath,
                #                     self.lrcconf,
                #                     resolution)
                # cachedfilepath = self.create_effect_lyric_file(cachedfilepath)
                self.create_songeffect_assfile(cachedfilepath)
            CachedContentDir.gdrive_file_upload(cachedfilepath)
            cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        return cachedfilepath

    def run(self, src: ContentFileInfo, **kwargs):
        cached_filename = LyricCachedFile.get_cached_filename(src.filename,
                                                              attribute=[self.lyricfile,
                                                                         self.lrcconf])
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        if cachedfilepath is None:
            cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            assfile = self.assfile.get()
            src = src.get()
            ffmpegcli.adding_sub_to_video(assfile,
                                          src,
                                          cachedfilepath)
            CachedContentDir.gdrive_file_upload(cachedfilepath)
            cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        return cachedfilepath

    def create_songeffect_assfile(self, output):
        with open(output, 'w') as ass_songeffect:
            self.lyricfile = GDriveMnger(True).download_file(self.lyricfile)
            with open(self.lyricfile, 'r') as lrcfile:
                lrcdata = lrcfile.read()
            data = generate_songeffect_for_lrc(self.songeffect.name, lrcdata, self.lrcconf)
            ass_songeffect.write(data)
        return output

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

            CachedContentDir.gdrive_file_upload(bg_cachedfile)
            bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        return bg_cachedfile

    def get_cached_bgvid(self, bgfile, time_length):
        cached_filename = BgVidCachedFile.get_cached_filename(bgfile.filename,
                                                              attribute=self.rendertype.configure,
                                                              extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            ffmpegcli = FfmpegCli()
            bgfile = bgfile.get()
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.create_media_file_from_img(input_img=bgfile,
                                                 time_length=time_length,
                                                 output_video=bgvid_cachedfile)
            CachedContentDir.gdrive_file_upload(bgvid_cachedfile)
            bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        return bgvid_cachedfile

    def render_background_based_timming(self):
        print('not support yet')

    def render_background_full_time_length(self):
        self.file: ContentFileInfo
        timeleng = self.rendertype.configure.duration
        self.input = self.file.get()  # initial input by background file
        if self.watermask:
            self.output = self.watermask.run(self.input)
            self.input = self.output
        if self.title:
            self.output = self.title.run(self.input)
            self.input = self.output
        if self.file:
            self.input = self.get_cached_backgroundimg()
            self.output = self.get_cached_bgvid(self.input, timeleng)
            self.input = self.output
        if self.effect:
            self.output = self.effect.run(self.input)
            self.input = self.output
        if self.spectrum:
            self.output = self.spectrum.run(self.input)
            self.input = self.output
        if self.lyric:
            self.output = self.lyric.run(self.input)
            self.input = self.output
        if self.song:
            self.output = self.song.run(self.input)
        return self.output.fileinfo

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
        self.file = None
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
        url_ret = ""
        for bgrender_engine in self.bgrenderengine:
            # TODO for now return for the first background render
            url_ret = bgrender_engine.run(bgrender_engine.input)
            telelog.debug("url return {} ".format(url_ret))
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
            if background_item.title:
                bgRender.title = RenderTitle(background_item.title)
            if background_item.lyric:
                lyricfile = self.songapi.song.lyric
                bgRender.lyric = RenderLyric(background_item.lyric,
                                             self.songapi.lyric,
                                             lyricfile,
                                             self.songapi.song_effect,
                                             bgRender.rendertype)
            if background_item.spectrum:
                bgRender.spectrum = RenderSpectrum(background_item.spectrum,
                                                   bgRender.rendertype)
            if background_item.watermask:
                bgRender.watermask = RenderWaterMask(background_item.watermask,
                                                     bgRender.rendertype)
            if self.songapi.song:
                bgRender.song = RenderSong(self.songapi.song)

            if background_item.timing:
                print('not support yet')

            self.bgrenderengine.append(bgRender)
            pass

    def __init__(self, renderdata):
        self.bgrenderengine = []
        self.songapi = SongApi(renderdata)
        self.generate_render_engine()
