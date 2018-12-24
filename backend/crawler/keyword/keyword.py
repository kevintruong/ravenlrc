from flashtext import *
from enum import IntEnum


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


class AssDialogueTextProcessor:
    def __init__(self, keyword: list) -> None:
        self.kwprocessor = KeywordProcessor()
        # self.kwprocessor.add_keywords_from_list(keyword)
        super().__init__()
