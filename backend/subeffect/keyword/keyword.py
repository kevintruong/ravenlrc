from flashtext import *
from enum import IntEnum
from backend.subeffect.asseffect.AnimatedTransform import *


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
        return "{{\\an{}}}".format(subalign)
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
        self.start = []
        self.end = []
        self.timing = None
        self.accel = 0.9

        for each_key in conf.keys():
            if 'start' in each_key:
                effect_start_info: dict = conf[each_key]
                for key, value in effect_start_info.items():
                    effect = self.get_effect(key, value)
                    if effect:
                        self.start.append(effect)
            elif 'end' in each_key:
                effect_start_info: dict = conf[each_key]
                for key, value in effect_start_info.items():
                    effect = self.get_effect(key, value)
                    if effect:
                        self.end.append(self.get_effect(key, value))
            elif 'timing' in each_key:
                if len(conf['timing']):
                    self.timing = conf['timing']
            elif 'accel' in each_key:
                self.accel = conf['accel']
            pass

    def create_full_animation_transform(self, timing_duration=None):
        if timing_duration is not None:
            timing = [0, timing_duration]
        else:
            timing = self.timing
        return self.animatedtransform.create_animation_transform(orgeffect=self.start,
                                                                 nexteffect=self.end,
                                                                 timing=timing,
                                                                 accel=self.accel)
        pass

    @classmethod
    def get_effect(cls, key, value):
        if key == 'font_size':
            return AnimatedEffect.FontSize(value)
        if key == 'primary_font_color':
            return AnimatedEffect.PrimaryFillColor(value)
        # TODO need to fill missing effect id

    @classmethod
    def json2dict(cls, effectinfo: dict):
        effect_start = []
        effect_end = []
        timing = []
        accel = None
        for key in effectinfo.keys():
            if 'start' == key:
                effect_start_info: dict = effectinfo[key]
                if len(effect_start_info):
                    for key, value in effect_start_info.items():
                        effect_start.append(cls.get_effect(key, value))
            if 'end' in key:
                trans_effect: dict = effectinfo[key]
                if len(trans_effect):
                    for key, value in trans_effect.items():
                        effect_end.append(cls.get_effect(key, value))
            if 'timing' == key:
                timing = effectinfo[key]
            if 'accel' == key:
                accel = effectinfo[key]
        return {
            'start': effect_start,
            'end': effect_end,
            'timming': timing,
            'accel': accel
        }


class AssDialogueTextFormatter:

    def __init__(self, formatinfo: dict) -> None:
        self.name = None
        self.color = None
        self.size = None
        self.newline = None
        self.align = None
        for key in formatinfo.keys():
            if key == 'name':
                self.name = formatinfo[key]
            if key == 'size':
                self.size = formatinfo[key]
            if key == 'color':
                self.color = formatinfo[key]
            if key == 'align':
                self.align = formatinfo[key]
            if key == 'newline':
                self.newline = formatinfo[key]

    def format_keyword(self, keyword: str):
        fontname_code = ""
        fontsize = ""
        fontcolor = ""
        subalign = ""
        if self.name:
            fontname_code = DialogueTextStyleCode.create_fontname_style_code(self.name)
        if self.size:
            fontsize = DialogueTextStyleCode.create_fontsize_style_code(self.size)
        if self.color:
            fontcolor = DialogueTextStyleCode.create_fontcolor_style_code(self.color)
        if self.align:
            subalign = DialogueTextStyleCode.create_subtitle_align_style_code(self.align)
        reset = DialogueTextStyleCode.create_reset_style_code()
        newword = fontname_code + fontsize + fontcolor + subalign + keyword + reset + '\\N'
        return newword

    def font_formatter(self):
        final_format_code = ""
        if self.name:
            fontname_code = DialogueTextStyleCode.create_fontname_style_code(self.name)
            final_format_code = final_format_code + fontname_code
        if self.size:
            fontsize = DialogueTextStyleCode.create_fontsize_style_code(self.size)
            final_format_code = final_format_code + fontsize
        if self.color:
            fontcolor = DialogueTextStyleCode.create_fontcolor_style_code(self.color)
            final_format_code = final_format_code + fontcolor
        if self.align:
            subalign = DialogueTextStyleCode.create_subtitle_align_style_code(self.align)
            final_format_code = final_format_code + subalign
        if self.newline:
            final_format_code = '\\N' + final_format_code
        return final_format_code


class AssDialogueTextProcessor:
    def __init__(self, keyword: list,
                 formatter=None,
                 animatedconf=None) -> None:
        self.keyword = keyword
        self.keywordformatter: AssDialogueTextFormatter = None
        self.keywordanimatedtransform: AssDialueTextAnimatedTransform = None
        if formatter:
            self.keywordformatter = formatter
        if animatedconf:
            self.keywordanimatedtransform = animatedconf
        super().__init__()

    def reconfig_keywords(self, duration=None):
        kwprocessor = KeywordProcessor()
        if self.keywordformatter:
            keyword_formatter = self.keywordformatter.font_formatter()
        else:
            keyword_formatter = ""
        if self.keywordanimatedtransform:
            animated_formatter = self.keywordanimatedtransform.create_full_animation_transform(duration)
        else:
            animated_formatter = ""

        reset = DialogueTextStyleCode.create_reset_style_code()
        for each_keyword in self.keyword:
            replace_keyword = keyword_formatter + animated_formatter + each_keyword
            if self.keywordformatter.newline:
                replace_keyword = replace_keyword + '\\N'
            # if self.keywordformatter.align:
            #     replace_keyword = replace_keyword + DialogueTextStyleCode.create_subtitle_align_style_code(
            #         self.keywordformatter.align)
            replace_keyword = replace_keyword + "{\\rDefault}"
            kwprocessor.add_keyword(each_keyword, replace_keyword)
        return kwprocessor

    def keyword_process(self, content, duration=None):
        kwprocessor = self.reconfig_keywords(duration)
        return kwprocessor.replace_keywords(content)
