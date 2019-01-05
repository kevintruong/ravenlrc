import json

# from backend.BackendCmderGdrive import *
#
import os


class TeleBuildCmder:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, cmder: str):
        cmd_args = cmder.split()
        if len(cmd_args) != 3:
            raise Exception("len of TeleCmder must be 3 {}".format(cmder))
        self.buildcmd = cmd_args[0]
        self.mvconfig = cmd_args[1]
        self.buildtype = cmd_args[2]
        self.is_buildtype_valid()
        self.is_configfile_exist()

    def is_configfile_exist(self):
        from backend.BackendCmder import ContentDir
        mvconfigdir = ContentDir.MVCONF_DIR.value
        for file in os.listdir(mvconfigdir):
            if self.mvconfig in file:
                self.mvconfig = os.path.join(ContentDir.MVCONF_DIR.value, file)
                return True
        raise Exception("not found Mvconfigure {} on ContentDir".format(self.mvconfig))

    def is_buildtype_valid(self):
        if self.buildtype in 'preview':
            self.buildtype = 0
            return True
        elif self.buildtype in 'release':
            self.buildtype = 1
            return True
        else:
            raise Exception('Build type {} not support yet'.format(self.buildtype))

    def run_build_cmd(self):
        from backend.BackendCmderGdrive import GDriveBuildCmder
        cmder = GDriveBuildCmder(self.mvconfig, self.buildtype)
        output = cmder.run()
        return output


import unittest


class TestTeleBuildCmder(unittest.TestCase):
    def setUp(self):
        self.telebuildcmder = TeleBuildCmder(r'/build TocGioThoiBay preview')

    def test_json_object(self):
        print(self.telebuildcmder.toJSON())

    def test_build_run(self):
        self.telebuildcmder.run_build_cmd()
