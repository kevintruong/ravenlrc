from abc import *
from threading import Thread, Event, Lock
import time

from Api.songeffect import generate_songeffect_for_lrc

from backend.storage.content import ContentFileInfo
from backend.type import SongInfo
from backend.utility.TempFileMnger import *
from backend.utility.Utility import clean_up, load_ass_from_lrc
from backend.yclogger import telelog, slacklog

from render.cache import *
from render.ffmpegcli import FfmpegCli
from render.parser import SongApi
from render.type import *

from publisher.facebook.fb_publish import FbPageAPI
from publisher.youtube.YoutubeMVInfo import YoutubeMVInfo
from publisher.youtube.YoutubeMVInfo import YtMvConfigSnippet
from publisher.youtube.youtube_uploader import YoutubeUploader
from publisher.youtube.youtube_uploader import YtMvConfigStatus


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
                                                                    self.songinfo.songfile.fileinfo['name']])
        effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            songfile = self.songinfo.songfile.get()
            src = src.get()
            leng = FfmpegCli().get_media_time_length(src)
            effectmv_cachedfile = MuxAudioVidCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            ffmpegcli.mux_audio_to_video(src,
                                         songfile,
                                         effectmv_cachedfile,
                                         leng)
            CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
            effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(cached_filename)
        return effectmv_cachedfile

    def __init__(self, songinfo: SongInfo, rendertype=None):
        super().__init__(rendertype)
        self.songinfo = songinfo


class RenderTiming:
    def __init__(self, timing):
        self.start = int(timing['start'])
        self.duration = int(timing['duration'])
        self.duration_ms = self.duration
        self.start_ms = self.start
        self.caculate_timming()

    @classmethod
    def format_timing(cls, ms):
        remainms = ms % 1000
        s = int(ms / 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return h, m, s, remainms

    def caculate_timming(self):
        curstartime = self.format_timing(self.start)
        duration = self.format_timing(self.duration)
        self.start = f'{curstartime[0]}:{curstartime[1]}:{curstartime[2]}.{curstartime[3]}'
        self.duration = f"{duration[0]}:{duration[1]}:{duration[2]}.{duration[3]}"


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

    def run(self, src: ContentFileInfo, **kwargs):
        renderfile_name = SecondBgImgCachedFile.get_file_name(src.filename,
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
            output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
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
        renderfile_name = SecondBgImgCachedFile.get_file_name(src.filename,
                                                              self.titleconf.file.filename,
                                                              self.titleconf.size)
        output = SecondBgImgCachedFile.get_cachedfile(renderfile_name)
        if not output:
            src = src.get()
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

        self.bgeffectfile = self.init_bgeffect_by_profile(profile)  # scale to render resolution
        effectfile_name = EffectCachedFile.get_cached_filename(self.bgeffectfile.filename,
                                                               attribute=[self.rendertype,
                                                                          self.timing],
                                                               extention='.mp4')

        cached_filename = BgEffectCachedFile.get_cached_filename(src.filename,
                                                                 attribute=[effectfile_name,
                                                                            self.bgEffect.opacity],
                                                                 extention='.mp4'
                                                                 )
        effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)
        if effect_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effect_cachedfile = BgEffectCachedFile.create_cachedfile(cached_filename)
            effect_file = self.bgeffectfile.get()
            effect_timelength = FfmpegCli().get_media_time_length(effect_file)
            src = src.get()
            ffmpegcli.add_effect_to_bg(effect_file,
                                       src,
                                       effect_cachedfile,
                                       self.bgEffect.opacity,
                                       effect_timelength)
            CachedContentDir.gdrive_file_upload(effect_cachedfile)
            effect_cachedfile = BgEffectCachedFile.get_cachedfile(cached_filename)

            effect_cachedfile = self.init_bgeffect_video_with_length(effect_cachedfile,
                                                                     timelength)
        return effect_cachedfile

    def __init__(self, bgeffect: BgEffect,
                 rendertype=None,
                 timing=None):
        super().__init__(rendertype)
        self.bgEffect = bgeffect
        self.bgeffectfile = None
        self.timing = timing

    def init_bgeffect_by_profile(self, profile):
        '''
        create background effect video scaled by profile
        :param profile:
        :return:
        '''
        # self.bgEffect.file = self.bgEffect.file.get()
        cached_filename = EffectCachedFile.get_cached_filename(self.bgEffect.file.fileinfo['name'],
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
                                                               attribute=[self.rendertype,
                                                                          self.timing],
                                                               extention='.mp4')
        effectmv_cachedfile = EffectCachedFile.get_cachedfile(cached_filename)
        if effectmv_cachedfile is None:
            ffmpegcli = FfmpegCli()
            effectprofilefile = effectprofilefile.get()
            effectmv_cachedfile = EffectCachedFile.create_cachedfile(cached_filename)
            ffmpegcli.create_background_affect_with_length(effectprofilefile,
                                                           effectmv_cachedfile,
                                                           length
                                                           )
            CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
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
                 rendertype=None,
                 timing=None):
        super().__init__(rendertype)
        self.lyric = lyric
        self.lrcconf = lrcconf
        self.lyricfile = lyricfile
        if songeffect:
            self.songeffect = songeffect
        self.assfile = self.generate_lyric_effect_file()
        self.timing: RenderTiming = timing

    def generate_lyric_effect_file(self):
        scale_factor = self.rendertype.configure.resolution.width / self.reference_resolution_width
        self.lrcconf.scale_font_size_by_factor(scale_factor)
        print(self.lyricfile)
        cached_filename = LyricCachedFile.get_cached_filename(self.lyricfile.fileinfo['name'],
                                                              attribute=[self.lrcconf,
                                                                         self.rendertype,
                                                                         self.songeffect],
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
            else:
                # TODO process non song effect
                pass
            CachedContentDir.gdrive_file_upload(cachedfilepath)
            cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        return cachedfilepath

    def run(self, src: ContentFileInfo, **kwargs):
        cached_filename = LyricCachedFile.get_cached_filename(src.fileinfo['name'],
                                                              attribute=[self.assfile.filename,
                                                                         self.lrcconf,
                                                                         self.rendertype,
                                                                         self.timing])
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        if cachedfilepath is None:
            if self.timing:
                return self.render_lyrics_by_timing(src, cached_filename)

            cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            assfile = self.assfile.get()
            src = src.get()
            ffmpegcli.adding_sub_to_video(assfile,
                                          src,
                                          cachedfilepath,
                                          timelength=self.rendertype.configure.duration,
                                          timing=self.timing)
            CachedContentDir.gdrive_file_upload(cachedfilepath)
            cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        return cachedfilepath

    def render_lyrics_by_timing(self, src: ContentFileInfo, cached_filename):
        cachedfilepath = LyricCachedFile.create_cachedfile(cached_filename)
        ffmpegcli = FfmpegCli()
        assfile = self.assfile.get()
        src = src.get()
        src_lenth = FfmpegCli().get_media_time_length(src)
        lyric_end = (self.timing.start_ms + self.timing.duration_ms) / 1000
        if src_lenth < lyric_end:
            newsrcfile = BgMvTemplateFile().getfullpath()
            FfmpegCli().create_background_affect_with_length(src, newsrcfile, lyric_end)
            src = newsrcfile
            pass
        ffmpegcli.adding_sub_to_video(assfile,
                                      src,
                                      cachedfilepath,
                                      timelength=self.rendertype.configure.duration,
                                      timing=self.timing)
        CachedContentDir.gdrive_file_upload(cachedfilepath)
        cachedfilepath = LyricCachedFile.get_cachedfile(cached_filename)
        return cachedfilepath
        pass

    def create_songeffect_assfile(self, output):
        with open(output, 'w') as ass_songeffect:
            self.lyricfile = self.lyricfile.get()
            with open(self.lyricfile, 'r') as lrcfile:
                lrcdata = lrcfile.read()
            data = generate_songeffect_for_lrc(self.songeffect.name,
                                               lrcdata,
                                               self.lrcconf,
                                               self.rendertype.configure.resolution)
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


class SongRenderEngine(ABC):

    def __init__(self, rendertype=None):
        if rendertype is None:
            self.rendertype = RenderType()
        else:
            self.rendertype = rendertype
        pass
        pass

    @abstractmethod
    def run(self, **kwargs):
        """
        abstract function to run song render
        :param kwargs:
        :return: FileInfo object (google drive file object)
        """
        pass


class BackgroundRender(RenderEngine):
    # TODO what if the background file is video
    # need another render object here.
    # 1. if img => return resolution video with timing (duration length)
    # 2. if video => format to render resolution, and scale timing by duration (timing)

    def __init__(self, file: ContentFileInfo, rendertype: RenderType, timing: RenderTiming):
        super().__init__()
        self.input = file
        self.rendertype = rendertype
        self.timing = None
        if timing:
            self.timing = timing
            self.timelength = int(timing.duration_ms / 100)  # ms => sec
        else:
            self.timelength = rendertype.configure.duration

    def is_video_mediafile(self, filepath):
        fileinfo = FileInfo(filepath)
        if fileinfo.ext.lower() in [".mp4", ".mov"]:
            return True
        elif fileinfo.ext.lower() in ['.jpg', '.png']:
            return False
        else:
            return False

        # media_info = MediaInfo.parse('my_video_file.mov')

    def get_cached_background(self):
        self.input: ContentFileInfo
        cached_filename = BgImgCachedFile.get_cached_filename(self.input.fileinfo.filename,
                                                              attribute=self.rendertype.configure.resolution)
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            self.input = self.input.get()
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
            ffmpegcli.create_media_file(input_img=bgfile,
                                        time_length=time_length,
                                        output_video=bgvid_cachedfile)
            CachedContentDir.gdrive_file_upload(bgvid_cachedfile)
            bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        return bgvid_cachedfile

    def format_bginput(self, inputfilepath):
        """
        from input file path => detect is video or image
        if image => convert to jpeg and scale to render resolution
        if video => scale to render resolution
        :param inputfilepath:
        :return:
        """
        self.input: ContentFileInfo = inputfilepath
        isvideo = self.is_video_mediafile(self.input.fileinfo['name'])
        if isvideo:
            cached_filename = BgImgCachedFile.get_cached_filename(self.input.fileinfo['name'],
                                                                  attribute=self.rendertype.configure.resolution)
        else:
            cached_filename = BgImgCachedFile.get_cached_filename(self.input.fileinfo['name'],
                                                                  attribute=self.rendertype.configure.resolution,
                                                                  extension='.jpg')

        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            ffmpegcli = FfmpegCli()
            self.input = self.input.get()
            ffmpegcli.scale_img_by_width_height(self.input,
                                                self.rendertype.configure.resolution,
                                                bg_cachedfile)
            CachedContentDir.gdrive_file_upload(bg_cachedfile)
            bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        return bg_cachedfile

        pass

    def run(self, src, **kwargs):
        """
        Scale to src to render resolution and scale live time to `timing.duration`
        :param src:
        :param kwargs:
        :return:
        """
        bgfile: ContentFileInfo = src
        cached_filename = BgVidCachedFile.get_cached_filename(bgfile.filename,
                                                              attribute=[self.rendertype.configure,
                                                                         self.timing],
                                                              extension='.mp4')
        bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        if bgvid_cachedfile is None:
            bgfile = self.format_bginput(bgfile)
            bgfile = bgfile.get()
            ffmpegcli = FfmpegCli()
            bgvid_cachedfile = BgVidCachedFile.create_cachedfile(cached_filename)
            isvideo = self.is_video_mediafile(bgfile)
            if isvideo:
                ffmpegcli.create_background_affect_with_length(bgfile, bgvid_cachedfile, self.timelength)
            else:
                ffmpegcli.create_media_file(input_img=bgfile,
                                            time_length=self.timelength,
                                            output_video=bgvid_cachedfile)
            CachedContentDir.gdrive_file_upload(bgvid_cachedfile)
            bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        return bgvid_cachedfile

        pass


class BackgroundItemRender(RenderEngine):

    def __init__(self,
                 songapi: SongApi,
                 background_item: Background):
        super().__init__()
        self.songapi = songapi
        self.output = None
        self.input = None
        self.watermask = None
        self.spectrum = None
        self.effect = None
        self.lyric = None
        self.title = None
        self.timing = None
        if background_item.timing:
            self.timing = background_item.timing
        if self.songapi.rendertype:
            self.rendertype = self.songapi.rendertype
        if background_item.file:
            self.file = background_item.file
            self.background = BackgroundRender(self.file,
                                               self.rendertype,
                                               self.timing)
        if background_item.effect:
            self.effect = RenderBgEffect(background_item.effect,
                                         self.rendertype)
        if background_item.title:
            self.title = RenderTitle(background_item.title,
                                     rendertype=self.rendertype)
        if background_item.lyric:
            lyricfile = self.songapi.song.lyric
            self.lyric = RenderLyric(background_item.lyric,
                                     self.songapi.lyric,
                                     lyricfile,
                                     self.songapi.song_effect,
                                     self.rendertype,
                                     self.timing)
        if background_item.spectrum:
            self.spectrum = RenderSpectrum(background_item.spectrum,
                                           self.rendertype)
        if background_item.watermask:
            self.watermask = RenderWaterMask(background_item.watermask,
                                             self.rendertype)

    def get_cached_backgroundimg(self):
        self.input: ContentFileInfo
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_filename(self.input.filename,
                                                              attribute=self.rendertype.configure.resolution,
                                                              extension='.jpg')
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            self.input = self.input.get()
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
            ffmpegcli.create_media_file(input_img=bgfile,
                                        time_length=time_length,
                                        output_video=bgvid_cachedfile)
            CachedContentDir.gdrive_file_upload(bgvid_cachedfile)
            bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        return bgvid_cachedfile

    def run(self, src: str, **kwargs):
        timeleng = self.rendertype.configure.duration
        self.input = self.file  # initial input by background file
        if self.watermask:
            self.output = self.watermask.run(self.input)
            self.input = self.output
        if self.title:
            self.output = self.title.run(self.input)
            self.input = self.output
        if self.file:
            self.output = self.background.run(self.input)
            self.input = self.output
        if self.effect:
            self.output = self.effect.run(self.input)
            self.input = self.output
        if self.spectrum:
            self.output = self.spectrum.run(self.input)
            self.input = self.output
        if self.lyric:
            self.output = self.lyric.run(self.input)
        return self.output


class SongMvSingleBackgroundRender(SongRenderEngine):

    def get_cached_backgroundimg(self):
        self.input: ContentFileInfo
        ffmpegcli = FfmpegCli()
        cached_filename = BgImgCachedFile.get_cached_filename(self.input.filename,
                                                              attribute=self.rendertype.configure.resolution,
                                                              extension='.jpg')
        bg_cachedfile = BgImgCachedFile.get_cachedfile(cached_filename)
        if bg_cachedfile is None:
            bg_cachedfile = BgImgCachedFile.create_cachedfile(cached_filename)
            self.input = self.input.get()
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
            ffmpegcli.create_media_file(input_img=bgfile,
                                        time_length=time_length,
                                        output_video=bgvid_cachedfile)
            CachedContentDir.gdrive_file_upload(bgvid_cachedfile)
            bgvid_cachedfile = BgVidCachedFile.get_cachedfile(cached_filename)
        return bgvid_cachedfile

    def run(self):
        output = self.bgitemRender.run(self.bgitemRender.file)
        if self.song:
            self.input = output
            self.output = self.song.run(self.input)
        return self.output

    def __init__(self, mvsongreq):
        super().__init__()
        self.songapi: SongApi = mvsongreq
        self.bgitemRender = BackgroundItemRender(self.songapi,
                                                 self.songapi.backgrounds[0])
        self.redertype: RenderType = None
        self.input = None
        self.output = None
        self.song: RenderSong = None
        self.init_render_engine()

    def init_render_engine(self):
        if 'publish' in self.songapi.rendertype.type:
            songfile = self.songapi.song.songfile.get()
            self.songapi.rendertype.configure.duration = FfmpegCli().get_media_time_length(songfile)
        if self.songapi.rendertype:
            self.rendertype = self.songapi.rendertype
        if self.songapi.song:
            self.song = RenderSong(self.songapi.song, self.rendertype)


class SongMvMultiBackground(SongRenderEngine):

    def __init__(self, rendersongreq: SongApi):
        super().__init__()
        self.songapi: SongApi = rendersongreq
        self.timinglist = []
        if self.songapi.song:
            self.song = RenderSong(self.songapi.song, self.rendertype)

    def generate_timing_list_by_option(self):
        lrcfile = self.songapi.song.lyric.get()
        songlength = self.songapi.song.timeleng
        asscontext = load_ass_from_lrc(lrcfile)
        ass_line_count = len(asscontext.events)
        bgitems_count = len(self.songapi.backgrounds)
        averave_len = int(ass_line_count / bgitems_count) + (ass_line_count % bgitems_count > 0.6)
        itemindex = list(range(0, ass_line_count - 1, averave_len))
        itemindex.append(ass_line_count - 1)

        for index, value in enumerate(itemindex):
            from backend.vendor.pysubs2 import SSAEvent
            cur_assevent: SSAEvent = asscontext.events[itemindex[index]]
            stop_assevent: SSAEvent = asscontext.events[itemindex[index + 1] - 1]
            end_assevent: SSAEvent = asscontext.events[itemindex[index + 1]]
            timing_nextstop = stop_assevent.end
            timing_start = cur_assevent.start
            timing_end = (end_assevent.start + timing_nextstop) / 2
            if index >= 1:
                stop_assevent: SSAEvent = asscontext.events[itemindex[index] - 1]
                cur_assevent: SSAEvent = asscontext.events[itemindex[index]]
                idle_duration = cur_assevent.start - stop_assevent.end
                timing_start = int(stop_assevent.end + idle_duration / 4)

            if index == 0:  # start => 0
                timing_start = 0

            if index == len(itemindex) - 2:  # endtiming -> songlength
                timing_end = songlength  # seconds => miliseconds
            timing = {
                'start': timing_start,
                'duration': int(timing_end - timing_start)
            }
            self.timinglist.append(RenderTiming(timing))
            if index == len(itemindex) - 2:  # endtiming -> songlength
                break

    def render(self, bgoutputs):
        clips = []
        filenames = []
        fade_in = 3
        fade_out = 2
        for output in bgoutputs:
            filenames.append(output.filename)
        filename = CachedFile.get_cached_filename(filenames[0],
                                                  attribute=[filenames, fade_in, fade_out],
                                                  extension='.mp4')
        effectmv_cachedfile = BgVidCachedFile.get_cachedfile(filename)
        if effectmv_cachedfile is None:
            effectmv_cachedfile = BgVidCachedFile.create_cachedfile(filename)
            for output in bgoutputs:
                from moviepy.editor import VideoFileClip
                from moviepy.video.fx.fadein import fadein
                from moviepy.video.fx.fadeout import fadeout
                bgoutput_filepath = output.get()
                thisclip = VideoFileClip(bgoutput_filepath)
                # crossfadein(fade_in). \
                # crossfadeout(fade_out)
                thisclip = fadein(thisclip, duration=fade_in)
                thisclip = fadeout(thisclip, duration=fade_out)
                clips.append(thisclip)
            import moviepy.editor as mp
            composite = mp.concatenate_videoclips(clips)
            # from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
            # composite = CompositeVideoClip(clips)
            composite.write_videofile(effectmv_cachedfile)
            # composition = Composition(clips, singletrack=True)
            # composition.save(effectmv_cachedfile)
            # CachedContentDir.gdrive_file_upload(effectmv_cachedfile)
            effectmv_cachedfile = MuxAudioVidCachedFile.get_cachedfile(filename)
        return self.song.run(effectmv_cachedfile)

    def render_without_timing(self):
        bgoutputs = []
        if self.songapi.autotiming is None:
            self.songapi.autotiming = 1
        self.generate_timing_list_by_option()
        for index, eachbgitem in enumerate(self.songapi.backgrounds):
            eachbgitem.timing = self.timinglist[index]
            bgrender = BackgroundItemRender(self.songapi, eachbgitem)
            bgoutput = bgrender.run(bgrender.file)
            bgoutputs.append(bgoutput)
        return self.render(bgoutputs)

        # TODO with each option of autotiming =>
        #  generate timing attribute for each background object
        # from `songapi` => get lrc => ass => loop in dialog event (list)

        pass

    def render_with_timing(self):
        pass

    def is_exist_timing(self):
        return False
        pass

    def generate_render_engine(self):
        has_timing = self.is_exist_timing()
        if has_timing:
            pass
        else:
            pass

    def run(self):
        if self.is_exist_timing():
            return self.render_with_timing()
        else:
            return self.render_without_timing()
        pass


class MvSongRender:
    def run(self):
        # TODO analyze render request => return render type:
        render: SongRenderEngine = self.generate_render_engine()
        url_ret = render.run()
        self.config_id = self.backup_config(url_ret.fileinfo['id'])
        self.output = url_ret
        return url_ret.fileinfo

    def get_kind_render_req(self):
        numof_bgs = len(self.songapi.backgrounds)
        if numof_bgs == 1:
            return SongMvType.SONGMV_SINGLE_BACKGROUND
        else:
            return SongMvType.SONGMV_MULTI_BACKGROUND
        pass

    def generate_render_engine(self):
        kindrender = self.get_kind_render_req()
        # kindrender = SongMvType.SONGMV_SINGLE_BACKGROUND
        if kindrender == SongMvType.SONGMV_MULTI_BACKGROUND:
            print("render multi-backgorund MV ")
            return SongMvMultiBackground(self.songapi)
        if kindrender == SongMvType.SONGMV_SINGLE_BACKGROUND:
            print('Render single background MV ')
            return SongMvSingleBackgroundRender(self.songapi)

    def backup_config(self, id: str):
        fileconfigname = '{}.json'.format(id)
        try:
            config_file = ContentDir.verify_file(ContentDir.MVCONF_DIR, fileconfigname)
        except Exception as exp:
            print('find not found => let upload new')
            config_file = None
        if config_file is None:
            config_file = os.path.join(ContentDir.MVCONF_DIR, fileconfigname)
            with open(config_file, 'w') as jsonfile:
                json.dump(self.renderdata, jsonfile, indent=4, sort_keys=True)
            fileinfo = ContentDir.gdrive_file_upload(config_file)
            id = fileinfo['id']
        else:
            telelog.info('already have configure file {}'.format(fileconfigname))
            if config_file.fileinfo is None:
                config_file.fileinfo = ContentDir.gdrive_file_upload(config_file.filepath)
            id = config_file.fileinfo['id']
        return id

    def __init__(self, renderdata):
        self.renderdata = renderdata
        self.bgrenderengine = []
        self.songapi = SongApi(renderdata)
        self.config_id = None
        self.output = None

    def set_publish_typte(self, typerender):
        self.songapi.rendertype = RenderType(typerender)


class RenderThread(Thread):
    def __init__(self, jsondata, typerender, channel='timshel'):
        super().__init__()
        self.config = jsondata
        self.song_render = MvSongRender(jsondata)
        self.song_render.set_publish_typte(typerender)
        self.daemon = True
        self.outputfile = None
        self.channel = channel

    def run(self) -> None:
        ret = self.song_render.run()
        self.outputfile = self.song_render.output
        self.youtube_publish()

    def youtube_publish(self):
        try:
            upload_mvfile = self.outputfile.get()
            songinfo = self.song_render.songapi.song
            handler = YoutubeUploader(self.channel)
            status = YtMvConfigStatus(3)
            snippet = YtMvConfigSnippet.create_snippet_from_info(YoutubeMVInfo(self.channel,
                                                                               songinfo))
            resp = handler.upload_video(upload_mvfile, snippet, status)
            self.facebook_publish(snippet, resp['id'])

        except Exception as exp:
            raise exp

    def facebook_publish(self, snippet, id: str):
        try:
            telelog.debug('facebook post {}'.format(id))
            upload_mvfile = self.outputfile.get()
            fbpage = FbPageAPI(self.channel)
            fbpage.post_video(snippet.to_dict(),
                              id,
                              upload_mvfile)
        except Exception as exp:
            from backend.yclogger import stacklogger
            from backend.yclogger import slacklog
            slacklog.error(stacklogger.format(exp))


class RenderThreadQueue(Thread):
    RenderQueue = None

    def __init__(self):
        super().__init__()
        self.renderqueue = []
        self.daemon = True
        self.event = Event()
        self.lock = Lock()

    @classmethod
    def get_renderqueue(cls):
        if cls.RenderQueue is None:
            cls.RenderQueue = RenderThreadQueue()
            cls.RenderQueue.start()
            return cls.RenderQueue
        else:
            return cls.RenderQueue

    def add(self, renderreq):
        self.lock.acquire()
        self.renderqueue.append(renderreq)
        self.lock.release()
        self.set_notify()

    def run(self) -> None:
        while True:
            while len(self.renderqueue):
                try:
                    print(len(self.renderqueue))
                    self.lock.acquire()
                    renderreq = self.renderqueue.pop()
                    self.lock.release()
                    telelog.info('render thread start')
                    renderreq: RenderThread
                    renderreq.start()
                    renderreq.join()
                    clean_up('/tmp/raven/cache')
                    clean_up('/tmp/raven/content')
                    telelog.info('render thread complete')
                except Exception as exp:
                    slacklog.error(exp)
            time.sleep(2)

    def set_notify(self):
        self.event.set()


import unittest


class Test_ThreadRenderQueue(unittest.TestCase):
    def test_renderthreadqueue_run(self):
        threadqueue = RenderThreadQueue.get_renderqueue()
        threadqueue.join()


class Test_RenderTiming(unittest.TestCase):
    def test_caculate_date(self):
        values = RenderTiming.format_timing(60050)
        print(values)

    def test_rendertiming(self):
        timing = RenderTiming({
            "start": "50000",
            "end": "40000"
        })
        print(timing.__dict__)
        leng_value = 50
        reference_len = 5
        averave_len = int(leng_value / reference_len) + (leng_value % reference_len > 0.6)
        itemindex = list(range(0, leng_value, averave_len))
        itemindex.append(leng_value)
        print(itemindex)
