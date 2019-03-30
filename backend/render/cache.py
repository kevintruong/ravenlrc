import hashlib
import os
from enum import Enum

from backend.storage.gdrive import GDriveStorage, GdriveCacheStorage
from backend.utility.Utility import FileInfo
from config.configure import BackendConfigure

config: BackendConfigure = BackendConfigure.get_config()
if config is None:
    CurDir = os.path.dirname(os.path.realpath(__file__))
    contentDir = os.path.join(CurDir, '../content')
    contentDir = os.path.abspath(contentDir)
    cachedcontentdir = contentDir
else:
    contentDir = os.path.join(config.StorageMountPoint, 'content')
    cachedcontentdir = os.path.join(config.CacheStorageMountPoint, 'cache')


class StorageInfo:
    def __init__(self, name, id, path):
        self.name = name
        self.id = id
        self.path = path


class ContentDir:
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
    WATERMASK_DIR = os.path.join(contentDir, 'Watermask')
    SPECTRUM_DIR = os.path.join(contentDir, 'Spectrum')
    CacheGDriveMappingDictCls = None

    def __init__(self):
        if self.CacheGDriveMappingDictCls is None:
            self.CacheGDriveMappingDict = {}
            cacheddirs = GDriveStorage.list_out('content')
            for each_dir in cacheddirs:
                if each_dir['name'] == 'Song':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.SONG_DIR)
                if each_dir['name'] == 'Effect':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.EFFECT_DIR)
                if each_dir['name'] == 'BgImage':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.BGIMG_DIR)
                if each_dir['name'] == 'Watermask':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.WATERMASK_DIR)
                if each_dir['name'] == 'Spectrum':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.BGIMG_DIR)
                if each_dir['name'] == 'ChannelInfo':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.CHANNELINFO_DIR)
                if each_dir['name'] == 'Title':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.TITLE_DIR)
                if each_dir['name'] == 'Mv':
                    mv_cacheddirs = GDriveStorage.list_out(fid=each_dir['id'])
                    for each_mv_dir in mv_cacheddirs:
                        if each_mv_dir['name'] == 'Preview':
                            self.CacheGDriveMappingDict[each_mv_dir['name']] = StorageInfo(each_dir['name'],
                                                                                           each_mv_dir['id'],
                                                                                           self.MVPREV_DIR)
                        if each_mv_dir['name'] == 'Release':
                            self.CacheGDriveMappingDict[each_mv_dir['name']] = StorageInfo(each_dir['name'],
                                                                                           each_mv_dir['id'],
                                                                                           self.MVRELEASE_DIR)
            ContentDir.CacheGDriveMappingDictCls = self.CacheGDriveMappingDict
        pass

    @classmethod
    def gdrive_file_pull(cls, dir, filename, output='/tmp'):
        if cls.CacheGDriveMappingDictCls is None:
            cls.CacheGDriveMappingDictCls = ContentDir().CacheGDriveMappingDict
        storeinfo: StorageInfo = cls.CacheGDriveMappingDictCls[dir]
        is_exists = GDriveStorage.is_file_exists_at_local(filename)
        if is_exists:
            listfiles = os.listdir(storeinfo.path)
            if filename in listfiles:
                return os.path.join(storeinfo.path, filename)
            else:
                parent_id = storeinfo.id
                fileinfo = GDriveStorage.viewFile(filename, parent_id)
                file_path = GDriveStorage.download_file(fileinfo['id'], storeinfo.path)
                return file_path
        else:
            parent_id = storeinfo.id
            fileinfo = GDriveStorage.viewFile(filename, parent_id)
            file_path = GDriveStorage.download_file(fileinfo['id'], storeinfo.path)
            return file_path

    @classmethod
    def gdrive_file_upload(cls,filepath):
        if cls.CacheGDriveMappingDictCls is None:
            cls.CacheGDriveMappingDictCls = ContentDir().CacheGDriveMappingDict
        dirname = os.path.basename(os.path.dirname(filepath))
        storeinfo: StorageInfo = cls.CacheGDriveMappingDictCls[dirname]
        fileinfo = GDriveStorage.upload_file(filepath, storeinfo.id)
        return fileinfo['webContentLink']


    @classmethod
    def get_file_path(cls, dir: str, filename: str):
        dir = os.path.basename(dir)
        try:
            file_path = cls.gdrive_file_pull(dir, filename)
            return file_path
        except Exception as exp:
            raise FileNotFoundError('Not found {} in {}'.format(filename, dir))


class CachedContentDir:
    SONG_DIR = os.path.join(cachedcontentdir, 'Song')
    EFFECT_DIR = os.path.join(cachedcontentdir, 'Effect')
    BGIMG_DIR = os.path.join(cachedcontentdir, 'BgImage')
    CacheGDriveMappingDictCls = None

    def __init__(self):
        if self.CacheGDriveMappingDictCls is None:
            self.CacheGDriveMappingDict = {}
            cacheddirs = GdriveCacheStorage.list_out('content')
            for each_dir in cacheddirs:
                if each_dir['name'] == 'Song':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.SONG_DIR)
                if each_dir['name'] == 'Effect':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.EFFECT_DIR)
                if each_dir['name'] == 'BgImage':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.BGIMG_DIR)
                if each_dir['name'] == 'Song':
                    self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                                                                                each_dir['id'],
                                                                                self.SONG_DIR)
                # if each_dir['name'] == 'Watermask':
                #     self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                 each_dir['id'],
                #                                                                 self.WATERMASK_DIR)
                # if each_dir['name'] == 'Spectrum':
                #     self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                 each_dir['id'],
                #                                                                 self.BGIMG_DIR)
                # if each_dir['name'] == 'ChannelInfo':
                #     self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                 each_dir['id'],
                #                                                                 self.CHANNELINFO_DIR)
                # if each_dir['name'] == 'Title':
                #     self.CacheGDriveMappingDict[each_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                 each_dir['id'],
                #                                                                 self.TITLE_DIR)
                # if each_dir['name'] == 'Mv':
                #     mv_cacheddirs = GDriveStorage.list_out(fid=each_dir['id'])
                #     for each_mv_dir in mv_cacheddirs:
                #         if each_mv_dir['name'] == 'Preview':
                #             self.CacheGDriveMappingDict[each_mv_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                            each_mv_dir['id'],
                #                                                                            self.MVPREV_DIR)
                #         if each_mv_dir['name'] == 'Release':
                #             self.CacheGDriveMappingDict[each_mv_dir['name']] = StorageInfo(each_dir['name'],
                #                                                                            each_mv_dir['id'],
                #                                                                            self.MVRELEASE_DIR)
            CachedContentDir.CacheGDriveMappingDictCls = self.CacheGDriveMappingDict
        pass




    @classmethod
    def gdrive_file_pull(cls, dir, filename, output='/tmp'):
        if cls.CacheGDriveMappingDictCls is None:
            cls.CacheGDriveMappingDictCls = CachedContentDir().CacheGDriveMappingDict
        storeinfo: StorageInfo = cls.CacheGDriveMappingDictCls[dir]
        is_exists = GdriveCacheStorage.is_file_exists_at_local(filename)
        if is_exists:
            listfiles = os.listdir(storeinfo.path)
            if filename in listfiles:
                return os.path.join(storeinfo.path, filename)
            else:
                parent_id = storeinfo.id
                fileinfo = GdriveCacheStorage.viewFile(filename, parent_id)
                file_path = GdriveCacheStorage.download_file(fileinfo['id'], storeinfo.path)
                return file_path
        else:
            listfiles = os.listdir(storeinfo.path)
            if filename in listfiles:
                filepath = os.path.join(storeinfo.path, filename)
                GdriveCacheStorage.upload_file(filepath, storeinfo.id)
                return filepath
            parent_id = storeinfo.id
            fileinfo = GdriveCacheStorage.viewFile(filename, parent_id)
            if len(fileinfo):
                file_path = GdriveCacheStorage.download_file(fileinfo['id'], storeinfo.path)
                return file_path
        return None

    @classmethod
    def get_file_path(cls, dir: str, filename: str):
        dir = os.path.basename(dir)
        try:
            file_path = cls.gdrive_file_pull(dir, filename)
            return file_path
        except Exception as exp:
            return None
            # raise FileNotFoundError('Not found {} in {}'.format(filename, dir))

    # @classmethod
    # def get_file_path(cls, dir: str, filename: str):
    #     listfiles = os.listdir(dir)
    #     for file in listfiles:
    #         if filename in file:
    #             return os.path.join(dir, file)
    #     return None


class CachedContentGdriveDir(Enum):

    def __init__(self):
        self.SONG_DIR = os.path.join(cachedcontentdir, 'Song')
        self.EFFECT_DIR = os.path.join(cachedcontentdir, 'Effect')
        self.BGIMG_DIR = os.path.join(cachedcontentdir, 'BgImage')

    @classmethod
    def get_file_path(cls, dir: str, filename: str):
        listfiles = os.listdir(dir)
        for file in listfiles:
            if filename in file:
                return os.path.join(dir, file)
        return None


class CachedFile:

    @classmethod
    def generate_hash_from_filename(cls, fname: str):
        name, ext = fname.split('.')
        hashfile = hashlib.md5(str(name + ext).encode('utf-8')).hexdigest()
        return hashfile + ".{}".format(ext)

    @classmethod
    def get_cached_filename(cls, filepath: str,
                            **kwargs):
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        cachedfilename = name
        added_ext = False
        for key, value in kwargs.items():
            if 'profile' == key:
                cachedfilename = cachedfilename + "_" + value
            if 'extension' == key:
                cachedfilename = cachedfilename + value
                added_ext = True
        if not added_ext:
            cachedfilename = cachedfilename + ext
        return cls.generate_hash_from_filename(cachedfilename)


class SongFile:
    CachedEffectDir = ContentDir.SONG_DIR

    @classmethod
    def get_fullpath(cls, filename):
        listfiles = os.listdir(cls.CachedEffectDir)
        for file in listfiles:
            if filename in file:
                return os.path.join(cls.CachedEffectDir, file)
        return None


class EffectCachedFile(CachedFile):
    CachedEffectDir = os.path.join(CachedContentDir.EFFECT_DIR)

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
    CachedDir = os.path.join(CachedContentDir.BGIMG_DIR)

    @classmethod
    def get_file_name(cls, bgimg: str, watermask: str, size):
        from backend.render.type import Size
        size: Size
        bgimg_name = FileInfo(bgimg).name
        ext = FileInfo(bgimg).ext
        watermask_name = FileInfo(watermask).name
        filename = bgimg_name + "_" + watermask_name + "_" + "{}".format(size.width) + "." + ext
        return cls.generate_hash_from_filename(filename)

        pass

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CachedDir, filename)
        # listfiles = os.listdir(cls.CachedDir)
        # for file in listfiles:
        #     if filename in file:
        #         return os.path.join(cls.CachedDir, file)
        # return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedDir, filename)


class MuxAudioVidCachedFile(CachedFile):
    CachedAudioVidDir = os.path.join(CachedContentDir.SONG_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CachedAudioVidDir, filename)
        # listfiles = os.listdir(cls.CachedAudioVidDir)
        # for file in listfiles:
        #     if filename in file:
        #         return os.path.join(cls.CachedAudioVidDir, file)
        # return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedAudioVidDir, filename)

    @classmethod
    def get_cached_file_name(cls, video, audio):
        videofilename = FileInfo(video).name
        audiofilename = FileInfo(audio).name
        bgeff_cachedfilename = videofilename + '_' + audiofilename + '.mp4'
        return cls.generate_hash_from_filename(bgeff_cachedfilename)


class BgEffectCachedFile(CachedFile):
    CachedEffectDir = os.path.join(CachedContentDir.EFFECT_DIR)
    BgEffectCachedDir = os.path.join(CachedEffectDir)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.BgEffectCachedDir, filename)
        # listfiles = os.listdir(cls.BgEffectCachedDir)
        # for file in listfiles:
        #     if filename in file:
        #         return os.path.join(cls.BgEffectCachedDir, file)
        # return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.BgEffectCachedDir, filename)

    @classmethod
    def get_cached_file_name(cls, previewbgmv, previeweffectmv, opacity_val=0):
        bgmv_fileinfo = FileInfo(previewbgmv)
        effmv_fileinfo = FileInfo(previeweffectmv)
        bgeff_cachedfilename = bgmv_fileinfo.name + '_' + effmv_fileinfo.name + str(opacity_val) + '.mp4'
        return cls.generate_hash_from_filename(bgeff_cachedfilename)


class BgImgCachedFile(CachedFile):
    CachedDir = os.path.join(CachedContentDir.BGIMG_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CachedDir, filename)
        # listfiles = os.listdir(cls.CachedDir)
        # for file in listfiles:
        #     if filename in file:
        #         return os.path.join(cls.CachedDir, file)
        # return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedDir, filename)

    pass


class BgVidCachedFile(CachedFile):
    CachedBgVidDir = os.path.join(CachedContentDir.BGIMG_DIR)

    @classmethod
    def get_cachedfile(cls, filename):
        return CachedContentDir.get_file_path(cls.CachedBgVidDir, filename)
        # listfiles = os.listdir(cls.CachedBgVidDir)
        # for file in listfiles:
        #     if filename in file:
        #         return os.path.join(cls.CachedBgVidDir, file)
        # return None

    @classmethod
    def create_cachedfile(cls, filename):
        return os.path.join(cls.CachedBgVidDir, filename)


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
