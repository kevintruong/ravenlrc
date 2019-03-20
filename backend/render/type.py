from enum import Enum, IntEnum
from backend.render.cache import ContentDir
from backend.subeffect.asseffect.LyricEffect import LyricEffect
from backend.utility.Utility import check_file_existed, PyJSON


class Size:
    def __init__(self, info: dict):
        self.width = int(info['width'])
        self.height = int(info['height'])


class Position:
    def __init__(self, info: dict):
        self.x = int(info['x'])
        self.y = int(info['y'])


class Font:
    def __init__(self, info: dict):
        self.name = info['name']
        self.color = int(info['color'], 16)
        self.size = int(info['size'])


class Lyric:
    def __init__(self, info: dict):
        self.file = None
        # self.effect = None
        self.words = []
        if 'file' in info:
            self.file = info['file']
        if 'words' in info:
            for wordeffect in info['words']:
                self.words.append(LyricEffect(wordeffect))
        pass


class Title(PyJSON):
    def __init__(self, d):
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.get_file_path(ContentDir.TITLE_DIR.value, self.file)


class Resolution(Size):
    def __init__(self, info: dict):
        super().__init__(info)


class RenderConfigure:
    def __init__(self, info: dict):
        for keyvalue in info.keys():
            if keyvalue == 'duration':
                self.duration = info[keyvalue]
            if keyvalue == 'resolution':
                self.resolution = Resolution(info[keyvalue])


class RenderType:
    def __init__(self, info=None):
        if info:
            for keyvalue in info.keys():
                if keyvalue == 'type':
                    self.type = info[keyvalue]
                if keyvalue == 'config':
                    self.configure = RenderConfigure(info[keyvalue])
        else:
            self.type = 'preview'
            self.configure = RenderConfigure({'duration': 90,
                                              'resolution': {'width': 1280, 'height': 720}
                                              })


class RenderTypeCode(Enum):
    BUILD_PREVIEW = "preview"
    BUILD_RELEASE = "release"


class Spectrum(PyJSON):
    def __init__(self, d):
        self.templatecode = None
        self.custom = None
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.get_file_path(ContentDir.SPECTRUM_DIR.value, self.file)


class BgSpectrum:
    def __init__(self, info: dict):
        for keyvalue in info.keys():
            if keyvalue == 'position':
                self.position = Position(info[keyvalue])
            if keyvalue == 'size':
                self.size = Size(info[keyvalue])


class BgEffect:
    def __init__(self, info: dict):
        from backend.render.cache import ContentDir
        self.file = ContentDir.get_file_path(ContentDir.EFFECT_DIR.value, info['file'])
        check_file_existed(self.file)
        self.opacity = int(info['opacity'])
        pass


class BgLyric:
    def __init__(self, info: dict):
        if 'position' in info:
            self.position = Position(info['position'])
        if 'size' in info:
            self.size = Size(info['size'])
        if 'font' in info:
            self.font = Font(info['font'])


class BgTitle(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class BgWaterMask(BgLyric):
    def __init__(self, info: dict):
        super().__init__(info)


class WaterMask(PyJSON):
    def __init__(self, d):
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.get_file_path(ContentDir.WATERMASK_DIR.value, self.file)


class MusicVideoKind(IntEnum):
    ALBUM_SINGLE_BACKGROUND = 0
    ALBUM_MULTI_BACKGROUND = 1
    MV_MULTI_BACKGROUND = 2
    MV_SINGLE_BACKGROUND = 3


class Background:
    def __init__(self, info: dict):
        self.file = None
        self.effect = None
        self.lyric = None
        self.title = None
        self.spectrum = None
        self.watermask = None
        self.timing = None
        for field in info.keys():
            if field == 'file':
                self.file = ContentDir.get_file_path(ContentDir.BGIMG_DIR.value, info[field])
                check_file_existed(self.file)
            elif field == 'effect':
                self.effect = BgEffect(info[field])
            elif field == 'lyric':
                self.lyric = BgLyric(info[field])
            elif field == 'watermask':
                self.watermask = BgWaterMask(info[field])
            elif field == 'title':
                self.title = BgTitle(info[field])
            elif field == 'spectrum':
                self.spectrum = BgSpectrum(info[field])
            elif field == 'timing':
                self.timing = info[field]
