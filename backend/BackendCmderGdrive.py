import os

import json5

from backend.BackendCmder import BuildCmder, ContentDir


class GDriveBuildCmder(BuildCmder):
    @classmethod
    def force_clearn_cache(cls):
        from sys import platform
        if platform == "linux" or platform == "linux2":
            try:
                from subprocess import call
                # call(["google-drive-ocamlfuse", "-cc", "-label", "me"])
                print('remount device')
                call(["fusermount", "-u", "/root/ytcreator/content"])
                call(["pkill", "google-drive-oc"])
                call(["google-drive-ocamlfuse", "-label", "me", "/root/ytcreator/content"])
            except Exception as e:
                print("{}".format(e))

    def __init__(self, configfile, buildtype=1):
        GDriveBuildCmder.force_clearn_cache()
        with open(configfile, 'r', encoding='UTF-8') as json5file:
            self.config = json5.load(json5file)
        self.config.update({'type': buildtype})
        self.config.update({'configfile': configfile})
        super().__init__(self.config)


import unittest


class test_load_mv_config(unittest.TestCase):
    def setUp(self):
        self.buildCmder = GDriveBuildCmder(
            os.path.join(ContentDir.MVCONF_DIR.value, 'gan_ngay_truoc_mat.json5'),
            1)
        pass

    def test_build_release(self):
        self.buildCmder.run()
        pass

    def test_reload(self):
        pass
