import os
import json5
from backend.BackendCmder import BackgroundInfo, EffectInfo, NctCrawler, SongInfo
from enum import Enum

CurDir = os.path.dirname(os.path.realpath(__file__))
contentDir = os.path.join(CurDir, 'content')


class ContentDir(Enum):
    SONG_DIR = os.path.join(contentDir, 'Song')
    EFFECT_DIR = os.path.join(contentDir, 'BgEffect')
    TITLE_DIR = os.path.join(contentDir, 'Title')
    MVCONF_DIR = os.path.join(contentDir, 'MvConfig')


class MvConfiguration:
    def __init__(self, configfile):
        self.song_url = None
        self.bg_info = None
        self.effect_info = None
        self.status = None
        self.song_info = None
        with open(configfile, 'r') as json5file:
            self.config = json5.load(json5file)
            for keyfield in self.config.keys():
                if 'song_url' in keyfield:
                    self.song_url = self.config[keyfield]
                if 'background_info' in keyfield:
                    self.bg_info = BackgroundInfo(self.config[keyfield])
                if 'effect_info' in keyfield:
                    self.effect_info = EffectInfo(self.config['effect_info'])
                if 'status' in keyfield:
                    self.status = self.config[keyfield]
        # self.crawl_song()

    def crawl_song(self):
        songinfo = NctCrawler(self.song_url).getdownload(ContentDir.SONG_DIR.value)
        self.song_info = SongInfo(songinfo)

    def build_mv(self):

        pass


import unittest


class Test_load_mv_config(unittest.TestCase):
    def setUp(self):
        self.mvConfig = MvConfiguration(os.path.join(ContentDir.MVCONF_DIR.value, 'nhammatthaymuahe.json5'))
        pass

    def test_crawl_song(self):
        songinfo = self.mvConfig.crawl_song()
        print(songinfo)

    pass
