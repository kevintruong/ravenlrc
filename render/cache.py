import hashlib
import json
import os

from backend.storage.content import CachedContentDir, ContentDir
from backend.utility.Utility import FileInfo, only_latin_string


class CachedFile:

    @classmethod
    def generate_hash_from_filename(cls, fname: str):
        name, ext = fname.split('.', -1)
        hashfile = hashlib.md5(str(name + ext).encode('utf-8')).hexdigest()
        return hashfile + ".{}".format(ext)

    @classmethod
    def get_cached_filename(cls, filepath: str,
                            **kwargs):
        fileinfo = FileInfo(filepath)
        name, ext = fileinfo.name, fileinfo.ext
        cachedfilename = name
        added_ext = False
        for key, value in kwargs.items():
            if 'profile' == key:
                cachedfilename = cachedfilename + "_" + value
            if 'extension' == key:
                cachedfilename = cachedfilename + value
                added_ext = True
            if 'attribute' == key:
                attribute = value
                str_attributes = json.dumps(attribute, default=lambda o: o.__dict__, sort_keys=True)
                str_attributes = only_latin_string(str_attributes)
                cachedfilename = cachedfilename + str_attributes
        if not added_ext:
            cachedfilename = cachedfilename + ext
        return cls.generate_hash_from_filename(cachedfilename)


class LyricMvCachedFile(CachedFile):
    CacheDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CacheDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CacheDir, filename)


class LyricCachedFile(CachedFile):
    CachedEffectDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CachedEffectDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedEffectDir, filename)


class EffectCachedFile(CachedFile):
    CacheDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CacheDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CacheDir, filename)


class SecondBgImgCachedFile(CachedFile):
    CachedDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_file_name(cls, bgimg: str, watermask: str, size):
        from render.type import Size
        size: Size
        bgimg_name = FileInfo(bgimg).name
        ext = FileInfo(bgimg).ext
        watermask_name = FileInfo(watermask).name
        filename = bgimg_name + "_" + watermask_name + "_" + "{}".format(size.width) + ext
        return cls.generate_hash_from_filename(filename)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CachedDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedDir, filename)


class MuxAudioVidCachedFile(CachedFile):
    CacheDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CacheDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CacheDir, filename)

    @classmethod
    def get_cached_file_name(cls, video, audio):
        videofilename = FileInfo(video).name
        audiofilename = FileInfo(audio).name
        bgeff_cachedfilename = videofilename + '_' + audiofilename + '.mp4'
        return cls.generate_hash_from_filename(bgeff_cachedfilename)


class BgEffectCachedFile(CachedFile):
    CacheDir = os.path.join(CachedContentDir.EFFECT_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CacheDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CacheDir, filename)

    @classmethod
    def get_cached_file_name(cls, previewbgmv, previeweffectmv, opacity_val=0):
        bgmv_fileinfo = FileInfo(previewbgmv)
        effmv_fileinfo = FileInfo(previeweffectmv)
        bgeff_cachedfilename = bgmv_fileinfo.name + '_' + effmv_fileinfo.name + str(opacity_val) + '.mp4'
        return cls.generate_hash_from_filename(bgeff_cachedfilename)


class BgImgCachedFile(CachedFile):
    CachedDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CachedDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedDir, filename)

    pass


class BgVidCachedFile(CachedFile):
    CacheDir = os.path.join(CachedContentDir.RENDER_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.verify_file(cls.CacheDir, filename)

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CacheDir, filename)


import unittest


class Test_CacheDir(unittest.TestCase):

    def setUp(self) -> None:
        self.cache = ContentDir()
        self.cachedrenderfile = CachedContentDir

    def test_cache_dir_acc(self):
        retval = self.cache.get_file_path(ContentDir.SONG_DIR, 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
        retval = self.cache.get_file_path('Song', 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
        retval = self.cache.get_file_path('Song', 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
        retval = self.cache.get_file_path('Song', 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
        retval = self.cache.get_file_path('Song', 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
        retval = self.cache.get_file_path('Song', 'Tự Nhiên Buồn_Hòa Minzy.mp3')
        print(retval)
