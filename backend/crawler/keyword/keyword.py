from flashtext import *
from enum import IntEnum
from backend.crawler.asseffect.AnimatedTransform import *


class SubtitleAlignment(IntEnum):
    SUB_ALIGN_LEFT_JUSTIFIED = 1
    SUB_ALIGN_CENTER_JUSTIFIED = 2
    SUB_ALIGN_RIGHT_JUSTIFIED = 3

    SUB_ALIGN_LEFT_JUSTIFIED_TOPTITLE = 5
    SUB_ALIGN_CENTER_JUSTIFIED_TOPTITLE = 6
    SUB_ALIGN_RIGHT_JUSTIFIED_TOPTITLE = 7

    SUB_ALIGN_LEFT_JUSTIFIED_MID_TITLE = 9
    SUB_ALIGN_CENTER_JUSTIFIED_MID_TITLE = 10
    SUB_ALIGN_RIGHT_JUSTIFIED_MID_TITLE = 11


class DialogueTextStyleCode:
    @classmethod
    def hex_to_rgb(cls, hexvar: int):
        hexstr = hex(hexvar)
        return tuple(hexstr[i:i + 2] for i in (2, 4, 6))

    @classmethod
    def create_fontname_style_code(cls, fontname: str):
        return "{{\\fn{}}}".format(fontname)

    @classmethod
    def create_fontsize_style_code(cls, fontsize):
        return "{{\\fs{}}}".format(fontsize)

    @classmethod
    def create_fontcolor_style_code(cls, colorcode: int):
        """

        :param colorcode: int hex rgb
        :return:
        """
        rgb = cls.hex_to_rgb(colorcode)
        return "{{\\c&{}{}{}&}}".format(rgb[2], rgb[1], rgb[0])

    @classmethod
    def create_subtitle_align_style_code(cls, subalign: SubtitleAlignment):
        return "{{\\a{}}}".format(subalign)
        pass

    @classmethod
    def create_reset_style_code(cls):
        return "{\\r}"
        pass


class KeyWorkd:
    def __init__(self) -> None:
        super().__init__()
        self.keyworkd = []


class AssDialueTextAnimatedTransform:
    def __init__(self, conf: dict):
        """
        effect : {'effect_id': EnumEffect,'effect_conf'=[<effect_conf>]}
        conf : dict
        conf {
            'pre':{ [] Pre Animation (effect before animated transform
            },
            'post': {[] Animated transform.
            },
            'timing': [t0,t1],
            'accel' : [0,1]
        }
        :param conf:
        """
        self.animatedtransform = AnimatedTransform()
        self.effect_start = None
        self.effect_transform = None
        self.timing = None
        self.accel = None

        for each_key in conf.keys():
            if 'effect_start' in each_key:
                self.effect_start = conf['effect_start']
            elif 'effect_transform' in each_key:
                self.effect_transform = conf['effect_transform']
            elif 'timing' in each_key:
                self.timing = conf['timing']
            elif 'accel' in each_key:
                self.accel = conf['accel']
            pass

    def create_full_transform(self):
        return self.animatedtransform.transform_from_effect_to_effect(orgeffect=self.effect_start,
                                                                      nexteffect=self.effect_transform,
                                                                      timing=Timing(self.timing[0], self.timing[1]),
                                                                      accel=self.accel)
        pass


class AssDialogueTextKeyWordFormatter:

    def __init__(self, formatinfo: dict) -> None:
        self.fontname = formatinfo['fontname']
        self.fontsize = formatinfo['fontsize']
        self.fontcolor = formatinfo['fontcolor']
        self.alignment = formatinfo['alignment']

    def format_keyword(self, keyword: str):
        fontname_code = DialogueTextStyleCode.create_fontname_style_code(self.fontname)
        fontsize = DialogueTextStyleCode.create_fontsize_style_code(self.fontsize)
        fontcolor = DialogueTextStyleCode.create_fontcolor_style_code(self.fontcolor)
        subalign = DialogueTextStyleCode.create_subtitle_align_style_code(self.alignment)
        reset = DialogueTextStyleCode.create_reset_style_code()
        newword = fontname_code + fontsize + fontcolor + subalign + keyword + reset + '\\N'
        return newword

    def font_formatter(self):
        fontname_code = DialogueTextStyleCode.create_fontname_style_code(self.fontname)
        fontsize = DialogueTextStyleCode.create_fontsize_style_code(self.fontsize)
        fontcolor = DialogueTextStyleCode.create_fontcolor_style_code(self.fontcolor)
        subalign = DialogueTextStyleCode.create_subtitle_align_style_code(self.alignment)
        return fontname_code + fontsize + fontcolor + subalign


class AssDialogueTextProcessor:
    def __init__(self, keyword: list, formatter: dict, animatedconf: dict) -> None:
        self.kwprocessor = KeywordProcessor()
        self.keyword = keyword
        self.keywordformatter = AssDialogueTextKeyWordFormatter(formatter)
        self.keywordanimatedtransform = AssDialueTextAnimatedTransform(animatedconf)
        self.__config_keywords()
        super().__init__()

    def __config_keywords(self):
        keyword_formatter = self.keywordformatter.font_formatter()
        animated_formatter = self.keywordanimatedtransform.create_full_transform()
        reset = DialogueTextStyleCode.create_reset_style_code()
        for each_keyword in self.keyword:
            replace_keyword = keyword_formatter + animated_formatter + each_keyword + reset
            self.kwprocessor.add_keyword(each_keyword, replace_keyword)

    def keyword_process(self, content):
        return self.kwprocessor.replace_keywords(content)
