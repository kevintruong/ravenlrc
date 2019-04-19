import abc
import json


class SongInfo:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, nctsonginfo=None):
        self.singer = None
        self.info = None
        self.title = None
        self.songfile = None
        self.lyrictext = None
        self.lyric = None
        self.id = None
        inputtype = type(nctsonginfo)
        if type(nctsonginfo) is dict:
            for keyvalue in nctsonginfo.keys():
                if keyvalue == 'singer':
                    self.singer = nctsonginfo[keyvalue]
                if keyvalue == 'info':
                    self.info = nctsonginfo[keyvalue]
                if keyvalue == 'title':
                    self.title = nctsonginfo[keyvalue]
                if keyvalue == 'songfile':
                    self.songfile = nctsonginfo[keyvalue]
                    from render.cache import SongFile
                    self.songfile = SongFile.get_fullpath(self.songfile)
                if keyvalue == 'id':
                    self.id = nctsonginfo[keyvalue]
                if keyvalue == 'lyrictext':
                    self.lyrictext = nctsonginfo[keyvalue]
                if keyvalue == 'lyric':
                    from render.cache import SongFile
                    self.lyric = nctsonginfo[keyvalue]
                    self.lyric = SongFile.get_fullpath(self.lyric)
        elif type(nctsonginfo) is tuple:
            self.id = nctsonginfo[0]
            self.singer = nctsonginfo[1]
            self.title = nctsonginfo[2]
            self.songfile = nctsonginfo[3]
            self.lyrictext = nctsonginfo[4]
            self.lyric = nctsonginfo[5]
            self.info = nctsonginfo[6]


class Cmder:
    def __init__(self):
        pass
        # self.effect: BgEffect = None
        # self.background: Background = None

    @abc.abstractmethod
    def run(self):
        pass
