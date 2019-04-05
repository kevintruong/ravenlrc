import abc
from enum import Enum


class RGB:
    @classmethod
    def hex_to_rgb(cls, hexvar: int):
        hexstr = hex(hexvar)
        return tuple(hexstr[i:i + 2] for i in (2, 4, 6))

    def __init__(self, hexvar: int):
        rgb = RGB.hex_to_rgb(hexvar)
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]


class FontEffect(Enum):
    FONT_SIZE = '\\fs'
    LETTER_SPACE = '\\fsp'
    PRIMARY_FILL_COLOR = '\\c'
    SECONDARY_FILL_COLOR = '\\2c'
    BORDER_FILL_COLOR = '\\3c'
    SHADOW_COLOR = '\\4c'
    PRIMARY_FILL_ALPHA = '\\a'
    SECONDARY_FILL_ALPHA = '\\2a'
    BORDER_FILL_ALPHA = '\\3a'
    SHADOWN_ALPHA = '\\4a'


class GeometryEffect(Enum):
    FONT_SCALE_X = '\\fscx'
    FONT_SCALE_Y = '\\fscy'
    TEXT_ROTATION_X = '\\frx'
    TEXT_ROTATION_Y = '\\fry'
    TEXT_ROTATION_Z = '\\frz'  # \fry-45 Rotate the text 45 degrees in opposite direction on the Y axis.
    TEXT_ROTATION = '\\fr'
    TEXT_SHEARING_X = '\\fax'
    TEXT_SHEARING_Y = '\\fay'


class OtherEffect(Enum):
    TEXT_BORDER_WIDTH = '\\bord'
    TEXT_BORDER_WIDTH_X = '\\xbord'
    TEXT_BORDER_WIDTH_Y = '\\ybord'
    TEXT_SHADOW_WIDTH = '\\shad'
    TEXT_SHADOW_WIDTH_X = '\\xshad'
    TEXT_SHADOW_WIDTH_Y = '\\yshad'
    TEXT_CLIP = '\\clip'
    TEXT_ICLIP = '\\iclip'
    TEXT_BLUR_EDGES = '\\be'
    TEXT_BLUR_EDGES_GAUSSIAN = '\\blur'


class AnimatedEffect:
    class Effect(abc.ABC):

        @abc.abstractmethod
        def get_effect_type_code(self):
            pass

    class FontScaleX(Effect):

        def get_effect_type_code(self):
            return self.effect_code + self.effect_value
            pass

        def set_effect_code(self):
            self.effect_code = GeometryEffect.FONT_SCALE_X.value

        def __init__(self, scale: int):
            self.effect_code = ""
            self.set_effect_code()
            self.effect_value = '{}'.format(scale)

    class FontScaleY(FontScaleX):

        def set_effect_code(self):
            self.effect_code = GeometryEffect.FONT_SCALE_Y.value

    class TextRotationd(Effect):
        def get_effect_type_code(self):
            return self.effect_type_code + self.effect_value
            pass

        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_ROTATION.value
            pass

        def __init__(self, value: int) -> None:
            self.effect_type_code = ""
            self.set_effect_type_code()
            self.effect_value = '{}'.format(value)
            pass

    class TextShearingX(Effect):
        def get_effect_type_code(self):
            return self.effect_type_code + self.effect_value
            pass

        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_SHEARING_X.value
            pass

        def __init__(self, value: float) -> None:
            self.effect_type_code = ""
            self.set_effect_type_code()
            self.effect_value = '{}'.format(value)
            pass

    class TextShearingY(TextShearingX):
        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_SHEARING_Y.value

    class TextRotationX(TextRotationd):

        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_ROTATION_X.value

    class TextRotationY(TextRotationd):

        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_ROTATION_Y.value

    class TextRotationZ(TextRotationd):

        def set_effect_type_code(self):
            self.effect_type_code = GeometryEffect.TEXT_ROTATION_Z.value

    class FontSize(Effect):

        def get_effect_type_code(self):
            return self.effect_code + str(self.effect_value)

        def __init__(self, config: int) -> None:
            super().__init__()
            self.effect_code = FontEffect.FONT_SIZE.value
            self.effect_value = config

    class LetterSpace(Effect):

        def get_effect_type_code(self):
            return self.effect_code + self.effect_param
            pass

        def __init__(self, space_param):
            self.effect_code = FontEffect.LETTER_SPACE.value
            self.effect_param = str(space_param)
            pass

    class PrimaryFillColor:
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: str):
            self.effect_code = FontEffect.PRIMARY_FILL_COLOR.value
            rgb = RGB(int(colorvalue, 16))
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class SecondaryFillColor:
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = FontEffect.SECONDARY_FILL_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class BorderFillColor:
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = FontEffect.BORDER_FILL_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class ShadowFillColor:
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = FontEffect.SHADOW_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class PrimaryFillAlpha(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = FontEffect.PRIMARY_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class SecondaryFillAlpha(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = FontEffect.SECONDARY_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class BorderFillAlpha(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = FontEffect.BORDER_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class ShadowFillAlpha(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = FontEffect.SHADOWN_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class Border(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_BORDER_WIDTH.value

        def __init__(self, borderval: int):
            self.effect_code = ""
            self.set_border_code_style()
            self.effect_param = "{}".format(borderval)
            pass

    class BorderX(Border):

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_BORDER_WIDTH_X.value

    class BorderY(Border):

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_BORDER_WIDTH_Y

    class ShadowDistance(Effect):
        def get_effect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_SHADOW_WIDTH.value

        def __init__(self, shadvalue: int):
            self.effect_code = ""
            self.set_border_code_style()
            self.effect_param = "{}".format(shadvalue)
            pass

    class ShadowDistanceX(ShadowDistance):

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_SHADOW_WIDTH_X.value

    class ShadowDistanceY(ShadowDistance):

        def set_border_code_style(self):
            self.effect_code = OtherEffect.TEXT_SHADOW_WIDTH_Y.value

    class RectangleClip(Effect):

        def get_effect_type_code(self):
            return self.effect_code + self.parameter
            pass

        def __init__(self, x1, y1, x2, y2):
            self.effect_code = OtherEffect.TEXT_CLIP.value
            self.parameter = "({},{},{},{})".format(x1, y1, x2, y2)
            pass

    class RectangleiClip(RectangleClip):

        def __init__(self, x1, y1, x2, y2):
            super().__init__(x1, y1, x2, y2)

    class BlurEdges(Effect):

        def get_effect_type_code(self):
            return self.effect_code + self.paramter

        def __init__(self, strength):
            self.effect_code = OtherEffect.TEXT_BLUR_EDGES.value
            self.paramter = '{}'.format(strength)

    class BlurEdgesGaussian(Effect):

        def get_effect_type_code(self):
            return self.effect_code + self.paramter
            pass

        def __init__(self, strength):
            self.effect_code = OtherEffect.TEXT_BLUR_EDGES_GAUSSIAN.value
            self.paramter = '{}'.format(strength)
