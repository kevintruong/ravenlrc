import json
import os

from backend.utility.Utility import PyJSON
from config.foldergenerator import SchemmaGenerator

curdir = os.path.dirname(os.path.realpath(__file__))
configfile = os.path.join(curdir, 'config.json')


class BackendConfigure(PyJSON):
    configfile = None

    def __init__(self, d):
        if self.configfile is None:
            self.StorageMountPoint = None
            self.CacheStorageMountPoint = None
            self.TmpDir = None
            super().__init__(d)
            self.configfile = self
            self.create_config_dir()

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
            if os.path.exists(configfile):
                with open(configfile, 'r') as conffile:
                    confdata = json.load(conffile)
                    return BackendConfigure(confdata).configfile
            else:
                return None
        else:
            return cls.configfile
