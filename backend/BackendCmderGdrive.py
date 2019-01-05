import os

import json5

from backend.BackendCmder import BuildCmder, ContentDir


class GDriveBuildCmder(BuildCmder):
    def __init__(self, configfile, buildtype=1):
        with open(configfile, 'r') as json5file:
            self.config = json5.load(json5file)
        self.config.update({'type': buildtype})
        super().__init__(self.config)


import unittest


class test_load_mv_config(unittest.TestCase):
    def setUp(self):
        self.buildCmder = GDriveBuildCmder(os.path.join(ContentDir.MVCONF_DIR.value, 'TocGioThoiBay.json5'),
                                           0)
        pass

    def test_build_release(self):
        self.buildCmder.run()
        pass
