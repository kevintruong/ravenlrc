import json5
import os

from backend.crawler.nct import SongInfo

cur_dir = os.path.dirname(os.path.realpath(__file__))
BuildCmderDir = os.path.join(cur_dir, '..\content\BuildCmd')


class MvDescription:
    def __init__(self, channelname: str, desname: str):
        self.channel = channelname
        self.desname = desname
        # self.songinfo = self.get_songinfo(buildmv)
        pass

    @staticmethod
    def get_mv_build_config(buildmv):
        buildmv = buildmv.replace(" ", "_")
        listfiles = os.listdir(BuildCmderDir)
        for file in listfiles:
            if buildmv in file:
                return os.path.join(BuildCmderDir, file)
        raise FileNotFoundError('Not found {} in {}'.format(buildmv, BuildCmderDir))

    def get_songinfo(self, buildmv):
        mvconfig_file = self.get_mv_build_config(buildmv)
        with open(mvconfig_file, 'r') as fileconfig:
            mvconfig = json5.load(fileconfig)
            if 'songinfo' in mvconfig:
                return mvconfig['songinfo']

    def description_formatter(self, header, footer, lyricfile):
        pass

    def create_snippet_obj(self, songinfo: SongInfo):
        title = r'[{}][Lyric][{}] {}'.format(self.channel, songinfo.singerTitle, songinfo.title)
        description = self.description_formatter(None, None, songinfo.lyric)
        pass

    def create_status_obj(self, delaydays):
        from backend.youtube.youtube_uploader import YtMvConfigStatus
        self.status = YtMvConfigStatus(delaydays)
        pass


import unittest


class TestMvDescription(unittest.TestCase):
    def setUp(self):
        self.mvDes = MvDescription('timeshel', 'Em à')

    def test_get_songinfo(self):
        songinfo = self.mvDes.get_songinfo('Em À')
        print(songinfo)
