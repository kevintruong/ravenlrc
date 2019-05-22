from backend.storage.content import SongFile
from backend.type import SongInfo
from backend.utility.Utility import *
from render.type import *


class SongApi:
    def __init__(self, jsondata: dict):
        super().__init__()
        self.watermask = None
        self.song = None
        self.song_url = None
        self.rendertype = RenderType()
        self.title = None
        self.watermask = None
        self.spectrum = None
        self.lyric = None
        self.autotiming = None
        for keyvalue in jsondata.keys():
            if keyvalue == 'song_url':
                self.song_url = jsondata[keyvalue]
            if keyvalue == 'song':
                self.song = SongInfo(jsondata[keyvalue])
            if keyvalue == 'backgrounds':
                self.backgrounds = self.get_list_background(jsondata[keyvalue])
            if keyvalue == 'lyric':
                self.lyric = Lyric(jsondata[keyvalue])
            if keyvalue == 'renderType':
                self.rendertype = RenderType(jsondata[keyvalue])
            if keyvalue == 'song_effect':
                self.song_effect = PyJSON(jsondata[keyvalue])
            if keyvalue == 'autotiming':
                self.autotiming = jsondata[keyvalue]
        self.get_song_info_from_url()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_song_info_from_url(self):
        if self.song is None and self.song_url:
            from Api.crawler import get_song_info
            songinfo = get_song_info(self.song_url)
            songinfo_dict = json.loads(songinfo)
            self.song = SongInfo(songinfo_dict)
            self.song.songinfo_retry_file()
            # self.song.songfile = SongFile.get_cachedfile(fid=self.song.songfile)
            # self.song.lyric = SongFile.get_cachedfile(fid=self.song.lyric)

    def get_list_background(self, info: list):
        backgrounds = []
        for background_info in info:
            background = Background(background_info)
            backgrounds.append(background)
        return backgrounds
