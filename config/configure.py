import json
import os

from backend.utility.Utility import PyJSON

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
