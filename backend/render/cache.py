import os
from enum import Enum

# from backend.render.type import Size
from backend.utility.Utility import FileInfo

CurDir = os.path.dirname(os.path.realpath(__file__))
contentDir = os.path.join(CurDir, '../content')
cachedcontentdir = os.path.join(CurDir, '../content')


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
    def get_cached_profile_filename(cls, filepath: str, profile=None, extension=None):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        cachedfilename = name
        if profile:
            cachedfilename = cachedfilename + "_" + profile
        if extension:
            cachedfilename = cachedfilename + extension
        else:
            cachedfilename = cachedfilename + ext
        return cachedfilename
        # return name + '_' + profile + ext


class SongFile:
    CachedEffectDir = ContentDir.SONG_DIR.value

    @classmethod
    def get_fullpath(cls, filename):
        listfiles = os.listdir(cls.CachedEffectDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.CachedEffectDir, file)
        return None


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


class SecondBgImgCachedFile(CachedFile):
    CachedDir = os.path.join(CachedContentDir.BGIMG_DIR.value, '.cache')

    @classmethod
    def get_file_name(cls, bgimg: str, watermask: str, size):
        from backend.render.type import Size
        size: Size
        bgimg_name = FileInfo(bgimg).name
        ext = FileInfo(bgimg).ext
        watermask_name = FileInfo(watermask).name
        return bgimg_name + "_" + watermask_name + "_" + "{}".format(size.width) + "." + ext

        pass

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
        audiofilename = FileInfo(audio).name
        bgeff_cachedfilename = videofilename + '_' + audiofilename + '.mp4'
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
