import ast
import json
from enum import Enum, IntEnum
from render.cache import ContentDir
from backend.utility.Utility import PyJSON


class Size:
    def __init__(self, info=None):
        if info:
            self.width = int(info['width'])
            self.height = int(info['height'])
        else:
            self.width = 1920
            self.height = 1080


class Position:
    def __init__(self, info: dict):
        self.x = int(info['x'])
        self.y = int(info['y'])


class Font:
    def __init__(self, info: dict):
        self.name = info['name']
        if '0x' in info['color'] or '0X' in info['color']:
            self.color: int = int(info['color'], 0)
        else:
            self.color: int = int(info['color'], 0)
        self.size = int(info['size'])
        self.name = self.get_fontname_from_file()

    def get_fontname_from_file(self):
        from config.configure import fontsdir
        import os
        fontfiles = os.listdir(fontsdir)
        for file in fontfiles:
            fontpath = os.path.join(fontsdir, file)
            if self.name in file:
                try:
                    fontname = self.get_font_name(fontpath)
                    return fontname
                except Exception as exp:
                    print('ignore this {}'.format(exp))
            try:
                fontname = self.get_font_name(fontpath)
                if self.name in fontname:
                    return fontname
            except Exception as exp:
                print('ignore this {}'.format(exp))
        raise FileNotFoundError('Not found {} font file'.format(self.name))

    def get_font_name(self, fontfile):
        from fontTools import ttLib
        """Get the short name from the font's names table"""
        FONT_SPECIFIER_NAME_ID = 4
        name = ""
        font = ttLib.TTFont(fontfile)
        for record in font['name'].names:
            try:
                if record.nameID == FONT_SPECIFIER_NAME_ID:
                    if b'\x00' in record.string:
                        name_str = record.string.decode('utf-16-be')
                    else:
                        name_str = record.string.decode('utf-8')
                    name = name_str
                if name:
                    break
            except Exception as exp:
                print('ignore the error {}'.format(exp))
                continue
        return name


import unittest


class Test_FontClass(unittest.TestCase):

    def test_fontinit(self):
        font = {'name': 'VL_Cimochi', 'color': '0xc68f8f', 'size': 60}
        VL_CimochiFont = Font(font)
        print(VL_CimochiFont.__dict__)


class Lyric:
    def __init__(self, info: dict):
        self.file = None
        self.words = []
        if 'file' in info:
            self.file = info['file']
        if 'words' in info:
            for wordeffect in info['words']:
                pass
                #  TODO support later
                # self.words.append(LyricEffect(wordeffect))
        pass


class Title(PyJSON):
    def __init__(self, d):
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.verify_file(ContentDir.TITLE_DIR, self.file)


class Resolution(Size):
    def __init__(self, info: dict):
        super().__init__(info)


class RenderConfigure:
    def __init__(self, info: dict):
        for keyvalue, value in info.items():
            if keyvalue == 'duration':
                self.duration = value
            if keyvalue == 'resolution':
                self.resolution = Resolution(value)

    def get_resolution_str(self):
        return '_'.join(str(attr) for attr in self.resolution.__dict__.values())


class RenderType:
    def __init__(self, info=None):
        self.type = None
        self.configure = None
        if info:
            for keyvalue, value in info.items():
                if keyvalue == 'type':
                    self.type = info[keyvalue]
                if keyvalue == 'config':
                    self.configure = RenderConfigure(info[keyvalue])
            if self.type and self.configure is None:
                if 'preview' in self.type:
                    self.configure = RenderConfigure(
                        {
                            'duration': 90,
                            'resolution': {
                                'width': 768,
                                'height': 432
                            }
                        }
                    )
                elif 'publish' in self.type:
                    self.configure = RenderConfigure(
                        {
                            'duration': 90,
                            'resolution': {
                                'width': 1920,
                                'height': 1080
                            }
                        }
                    )
        else:
            self.type = 'preview'
            self.configure = RenderConfigure(
                {
                    'duration': 90,
                    'resolution': {
                        'width': 1280,
                        'height': 720
                    }
                }
            )


class RenderTypeCode(Enum):
    BUILD_PREVIEW = "preview"
    BUILD_RELEASE = "release"


class Spectrum(PyJSON):
    def __init__(self, d):
        self.templatecode = None
        self.custom = None
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.verify_file(ContentDir.SPECTRUM_DIR, self.file)


class BgSpectrum:
    def __init__(self, info: dict):
        self.templatecode = None
        self.custom = None
        for key, value in info.items():
            if key == 'file':
                self.file = ContentDir.verify_file(ContentDir.SPECTRUM_DIR, value)
            if key == 'position':
                self.position = Position(value)
            if key == 'size':
                self.size = Size(value)
            if key == 'custom':
                self.custom = PyJSON(value)
                print('TODO not support yet')
            if key == 'templatecode':
                self.templatecode = value


class BgEffect:
    def __init__(self, info: dict):
        for key, value in info.items():
            if key == 'file':
                self.file = ContentDir.verify_file(ContentDir.EFFECT_DIR, value)
            if key == 'opacity':
                self.opacity = int(str(value))


class BgLyric:
    def __init__(self, info: dict):
        if 'position' in info:
            self.position = Position(info['position'])
        if 'size' in info:
            self.size = Size(info['size'])
        if 'font' in info:
            self.font = Font(info['font'])

    def scale_font_size_by_factor(self, factor: float):
        self.font.size = int(self.font.size * factor)
        self.size.height = int(self.size.height * factor)
        self.size.width = int(self.size.width * factor)
        self.position.x = int(self.position.x * factor)
        self.position.y = int(self.position.y * factor)

    def toJSON(self):
        data = json.dumps(self, default=lambda o: o.__dict__)
        return ast.literal_eval(data)


class BgTitle:
    def __init__(self, info: dict):
        for key, value in info.items():
            if key == 'file':
                self.file = ContentDir.verify_file(ContentDir.TITLE_DIR, value)
                continue
            if key == 'text':
                self.text = value
                continue
            if key == 'position':
                self.position = Position(value)
                continue
            if key == 'size':
                self.size = Size(value)
                continue
            if key == 'font':
                self.font = Font(value)
                continue


class BgWaterMask:
    def __init__(self, info: dict):
        for key, value in info.items():
            if key == 'file':
                self.file = ContentDir.verify_file(ContentDir.WATERMASK_DIR, value)
                continue
            if key == 'text':
                self.text = value
                continue
            if key == 'position':
                self.position = Position(value)
                continue
            if key == 'size':
                self.size = Size(value)
                continue
            if key == 'font':
                self.font = Font(value)
                continue


class WaterMask(PyJSON):
    def __init__(self, d):
        super().__init__(d)
        if 'file' in self.__dict__:
            self.file = ContentDir.verify_file(ContentDir.WATERMASK_DIR, self.file)


class SongMvType(IntEnum):
    SONGMV_MULTI_BACKGROUND = 2
    SONGMV_SINGLE_BACKGROUND = 3


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
                self.file = ContentDir.verify_file(ContentDir.BGIMG_DIR, info[field])
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
