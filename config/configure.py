import json
import os

from config.foldergenerator import SchemmaGenerator

curdir = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(curdir, 'config.json')
fontsdir = os.path.abspath(os.path.join(curdir, '../.fonts'))


class BackendConfigure:
    configfile = None

    def __init__(self, info: dict):
        if BackendConfigure.configfile is None:
            self.StorageMountPoint = None
            self.CacheStorageMountPoint = None
            self.TmpDir = None
            for key, value in info.items():
                if key == 'StorageMountPoint':
                    self.StorageMountPoint = value
                if key == 'CacheStorageMountPoint':
                    self.CacheStorageMountPoint = value
                if key == 'TmpDir':
                    self.TmpDir = value
            self.create_config_dir()
            self.fontsdir = fontsdir
            BackendConfigure.configfile = self
            from ffmpegbin import ffmpegbin
            os.environ['FFMPEG_BINARY'] = os.path.join(ffmpegbin.ffmpegpath, 'ffmpeg')

    def create_dir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                return True
        except OSError:
            print('Error: Creating directory. ' + path)
            return False

    def create_config_dir(self):
        if self.StorageMountPoint:
            self.create_dir(self.StorageMountPoint)
        if self.CacheStorageMountPoint:
            self.create_dir(self.CacheStorageMountPoint)
        if self.TmpDir:
            self.create_dir(self.TmpDir)
        SchemmaGenerator(os.path.join(curdir, 'CacheStorageDirMap.json'),
                         self.CacheStorageMountPoint).generate()
        SchemmaGenerator(os.path.join(curdir, 'StorageDirMap.json'), self.StorageMountPoint).generate()

    @classmethod
    def get_config(cls):
        if cls.configfile is None:
            print('first configure')
            if os.path.exists(configfile):
                with open(configfile, 'r') as conffile:
                    confdata = json.load(conffile)
                    return BackendConfigure(confdata).configfile
            else:
                return None
        else:
            print('allready configured')
            return cls.configfile


import unittest


class Test_Configure(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test_configure(self):
        BackendConfigure.get_config()
        config = BackendConfigure.get_config()
        print(config)
