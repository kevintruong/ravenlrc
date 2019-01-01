import os

import json5

from backend.BackendCmder import BuildCmder, ContentDir


class GDriveBuildCmder(BuildCmder):
    def __init__(self, configfile):
        with open(configfile, 'r') as json5file:
            self.config = json5.load(json5file)
        super().__init__(self.config)


import unittest


class test_load_mv_config(unittest.TestCase):
    def setUp(self):
        pass

    def test_init_MvConfigure(self):
        self.mvConfig = GDriveBuildCmder(os.path.join(ContentDir.MVCONF_DIR.value, 'nhammatthaymuahe.json5'))
