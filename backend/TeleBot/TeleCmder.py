import json

# from backend.BackendCmderGdrive import *
#
import os

from backend.facebook.fb_publish import FbPageAPI


class TelePublishCmder:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, cmder: str):
        from backend.BackendCmderGdrive import GDriveBuildCmder
        from backend.youtube.youtube_uploader import YoutubeUploader
        cmd_args = cmder.split()
        self.publishcmd = cmd_args[0]
        self.mvconfig = cmd_args[1]
        self.is_configfile_exist()
        self.channel = cmd_args[2]
        self.cmder = GDriveBuildCmder(self.mvconfig_file, 1)
        self.ythandler = YoutubeUploader(self.channel)
        self.fbpage = FbPageAPI(self.channel)

    def is_configfile_exist(self):
        from backend.BackendCmder import ContentDir
        mvconfigdir = ContentDir.MVCONF_DIR.value
        for file in os.listdir(mvconfigdir):
            if self.mvconfig.lower() in file.lower():
                self.mvconfig_file = os.path.join(ContentDir.MVCONF_DIR.value, file)
                return True
        raise Exception("not found Mvconfigure {} on ContentDir".format(self.mvconfig))

    def publish_mv_to_channel(self):
        from backend.youtube.youtube_uploader import YtMvConfigStatus
        from backend.youtube.YoutubeMVInfo import YtMvConfigSnippet
        from backend.youtube.YoutubeMVInfo import YoutubeMVInfo

        status = YtMvConfigStatus(3)
        snippet = YtMvConfigSnippet.create_snippet_from_info(YoutubeMVInfo(self.channel,
                                                                           self.mvconfig))
        resp = self.ythandler.upload_video(self.cmder.output, snippet, status)
        self.fbpage.post_yt_mv_des(resp['snippet'], resp['id'])
        pass

    def run_publish_cmd(self):
        from backend.utility.Utility import check_file_existed
        try:
            check_file_existed(self.cmder.output)
        except Exception as exp:
            print('mv file {} not build release yet => Build the release'.format(self.cmder.output))
            self.cmder.run()
            check_file_existed(self.cmder.output)
        self.publish_mv_to_channel()


#       Run publish Youtube API command


class TeleBuildCmder:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, cmder: str):
        cmd_args = cmder.split()
        self.buildcmd = cmd_args[0]
        self.mvconfig = cmd_args[1]
        if len(cmd_args) < 3:
            self.buildtype = 'preview'
        else:
            self.buildtype = cmd_args[2]
        self.is_buildtype_valid()
        self.is_configfile_exist()

    def is_configfile_exist(self):
        from backend.BackendCmder import ContentDir
        mvconfigdir = ContentDir.MVCONF_DIR.value
        for file in os.listdir(mvconfigdir):
            if self.mvconfig.lower() in file.lower():
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
            print('Build type {} not support yet'.format(self.buildtype))
            print('select default build type: Preview')
            self.buildtype = 0

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


class TestTeleGramPublishCmder(unittest.TestCase):
    def setUp(self):
        pass

    def test_publish_run(self):
        self.publishcmder = TelePublishCmder('r/publish huyen_thoai timshel')
        self.publishcmder.run_publish_cmd()

    def test_publish_nhe(self):
        self.publishcmder = TelePublishCmder('r/publish nhe timshel')
        self.publishcmder.run_publish_cmd()
