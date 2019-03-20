# from backend.render.cache import ContentDir
from backend.subeffect.asseditor import LyricConfigInfo
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


class TitleInfo(LyricConfigInfo):

    def __init__(self, titleinfo: dict):
        super().__init__(titleinfo)


class BackgroundInfo:
    def __init__(self, bginfo: dict):
        for keyfield in bginfo.keys():
            if 'bg_file' in keyfield:
                from backend.render.cache import ContentDir
                self.bg_file = ContentDir.get_file_path(ContentDir.BGIMG_DIR.value, bginfo[keyfield])
                check_file_existed(self.bg_file)
            if 'lyric_info' in keyfield:
                self.subinfo: LyricConfigInfo = LyricConfigInfo(bginfo[keyfield])
            if 'title_info' in keyfield:
                self.titleinfo = TitleInfo(bginfo[keyfield])


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


class Spectrum(PyJSON):
    def __init__(self, d):
        self.templatecode = None
        self.custom = None
        super().__init__(d)


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


class BgWaterMask:
    def __init__(self, info: dict):
        self.file = info['file']
        self.position = Position(info['position'])


class BgLyric:
    def __init__(self, info: dict):
        if 'position' in info:
            self.position = Position(info['position'])
        if 'size' in info:
            self.size = Size(info['size'])
        if 'font' in info:
            self.font = Font(info['font'])


class Title(PyJSON):
    def __init__(self, d):
        super().__init__(d)


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
