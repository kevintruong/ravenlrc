import abc
import json

from backend.storage.content import SongFile


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
        self.timeleng = None
        inputtype = type(nctsonginfo)
        if inputtype is str:
            nctsonginfo = json.loads(nctsonginfo)
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
                if keyvalue == 'id':
                    self.id = nctsonginfo[keyvalue]
                if keyvalue == 'lyrictext':
                    self.lyrictext = nctsonginfo[keyvalue]
                if keyvalue == 'lyric':
                    self.lyric = nctsonginfo[keyvalue]
                if keyvalue == 'timeleng':
                    self.timeleng = nctsonginfo[keyvalue]
        elif type(nctsonginfo) is tuple:
            self.id = nctsonginfo[0]
            self.singer = nctsonginfo[1]
            self.title = nctsonginfo[2]
            self.songfile = nctsonginfo[3]
            self.lyrictext = nctsonginfo[4]
            self.lyric = nctsonginfo[5]
            self.info = nctsonginfo[6]
            if len(nctsonginfo) > 7:
                self.timeleng = nctsonginfo[7]

    def verify_songinfo(self):
        self.songfile = SongFile.get_cachedfile(fid=self.songfile)
        self.lyric = SongFile.get_cachedfile(fid=self.lyric)
        if self.timeleng == 0:
            raise Exception('Timelength return error')


class Cmder:
    def __init__(self):
        pass
        # self.effect: BgEffect = None
        # self.background: Background = None

    @abc.abstractmethod
    def run(self):
        pass
