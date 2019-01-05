import json

from backend.BackendCmderGdrive import *

mvconfigdir = ContentDir.MVCONF_DIR.value


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
        for file in os.listdir(ContentDir.MVCONF_DIR.value):
            if self.mvconfig in file:
                self.mvconfig = os.path.join(ContentDir.MVCONF_DIR.value, file)
                return True
        raise Exception("not found Mvconfigure {} on ContentDir".format(self.mvconfig))

    def is_buildtype_valid(self):
        if self.buildtype in 'preview':
            return True
        elif self.buildtype in 'release':
            return True
        else:
            raise Exception('Build type {} not support yet'.format(self.buildtype))

    def run_build_cmd(self):
        cmder = GDriveBuildCmder(self.mvconfig)
        cmder.run()


import unittest


class TestTeleBuildCmder(unittest.TestCase):
    def setUp(self):
        self.telebuildcmder = TeleBuildCmder(r'/build TocGioThoiBay preview')

    def test_json_object(self):
        print(self.telebuildcmder.toJSON())

    def test_build_run(self):
        self.telebuildcmder.run_build_cmd()
