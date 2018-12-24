from enum import *
import abc


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


class AnimationTransform:
    class FontAffect(Enum):
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

    class GeometryAffect(Enum):
        FONT_SCALE_X = '\\fscx'
        FONT_SCALE_Y = '\\fscy'
        TEXT_ROTATION_X = '\\frx'
        TEXT_ROTATION_Y = '\\fry'
        TEXT_ROTATION_Z = '\\frz'  # \fry-45 Rotate the text 45 degrees in opposite direction on the Y axis.
        TEXT_SHEARING_X = '\\fax'
        TEXT_SHEARING_Y = '\\fay'

    class OtherAffect(Enum):
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

    class Affect(abc.ABC):

        @abc.abstractmethod
        def get_affect_type_code(self):
            pass

    class FontSize(Affect):

        def get_affect_type_code(self):
            return self.effect_code + str(self.effect_value)

        def __init__(self, config: str) -> None:
            super().__init__()
            self.effect_code = AnimationTransform.FontAffect.FONT_SIZE.value
            self.effect_value = config

    class LetterSpace(Affect):

        def get_affect_type_code(self):
            return self.effect_code + self.effect_param
            pass

        def __init__(self, space_param):
            self.effect_code = AnimationTransform.FontAffect.LETTER_SPACE.value
            self.effect_param = str(space_param)
            pass

    class PrimaryFillColor:
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = AnimationTransform.FontAffect.PRIMARY_FILL_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class SecondaryFillColor:
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = AnimationTransform.FontAffect.SECONDARY_FILL_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class BorderFillColor:
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = AnimationTransform.FontAffect.BORDER_FILL_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class ShadowFillColor:
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, colorvalue: int):
            self.effect_code = AnimationTransform.FontAffect.SHADOW_COLOR.value
            rgb = RGB(colorvalue)
            self.effect_param = "H{}{}{}".format(rgb.b, rgb.g, rgb.r)
            pass

    class PrimaryFillAlpha(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = AnimationTransform.FontAffect.PRIMARY_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class SecondaryFillAlpha(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = AnimationTransform.FontAffect.SECONDARY_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class BorderFillAlpha(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = AnimationTransform.FontAffect.BORDER_FILL_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class ShadowFillAlpha(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def __init__(self, alphavalue: int):
            self.effect_code = AnimationTransform.FontAffect.SHADOWN_ALPHA.value
            alpha = hex(alphavalue)[2:4]
            self.effect_param = "H{}".format(alpha)
            pass

    class Border(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_BORDER_WIDTH.value

        def __init__(self, borderval: int):
            self.effect_code = ""
            self.set_border_code_style()
            self.effect_param = "{}".format(borderval)
            pass

    class BorderX(Border):

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_BORDER_WIDTH_X.value

    class BorderY(Border):

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_BORDER_WIDTH_Y

    class ShadowDistance(Affect):
        def get_affect_type_code(self):
            return self.effect_code + "&{}&".format(self.effect_param)
            pass

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_SHADOW_WIDTH.value

        def __init__(self, shadvalue: int):
            self.effect_code = ""
            self.set_border_code_style()
            self.effect_param = "{}".format(shadvalue)
            pass

    class ShadowDistanceX(ShadowDistance):

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_SHADOW_WIDTH_X.value

    class ShadowDistanceY(ShadowDistance):

        def set_border_code_style(self):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_SHADOW_WIDTH_Y

    class RectangleClip(Affect):

        def get_affect_type_code(self):
            return self.effect_code + self.parameter
            pass

        def __init__(self, x1, y1, x2, y2):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_CLIP.value
            self.parameter = "({},{},{},{})".format(x1, y1, x2, y2)
            pass

    class RectangleiClip(RectangleClip):

        def __init__(self, x1, y1, x2, y2):
            super().__init__(x1, y1, x2, y2)

    class BlurEdges(Affect):

        def get_affect_type_code(self):
            pass

        def __init__(self, strength):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_BLUR_EDGES.value
            self.paramter = '{}'.format(strength)

    class BlurEdgesGaussian(Affect):

        def get_affect_type_code(self):
            pass

        def __init__(self, strength):
            self.effect_code = AnimationTransform.OtherAffect.TEXT_BLUR_EDGES_GAUSSIAN.value
            self.paramter = '{}'.format(strength)

    class Timing:
        def __init__(self, t0: int, t1: int) -> None:
            super().__init__()
            self.t0 = t0
            self.t1 = t1

    def __init__(self) -> None:
        super().__init__()
        self.animationtransform_typecode = '\\t'

    def linear_transform(self, affectlist: [Affect]):
        # linear transform from before /t to after /t animation
        # {\1c&HFF0000&\t(\1c&H0000FF&)}Hello!
        # The text starts out blue,
        # but fades towards red so it is completely red when the line ends.
        effecttypecodes = ""
        for each in affectlist:
            code_style = each.get_affect_type_code()
            effecttypecodes += code_style
        return "\\t{{{}}}".format(effecttypecodes)
        pass

    def non_linear_transform(self, affectlist: [Affect], accel=0):
        # non linear transform from before /t to after /t animation
        # \t{(0.5,\frz3600)}Wheel # transform accel 0.5 (non linear) frz3600
        effecttypecodes = ""
        for each in affectlist:
            code_style = each.get_affect_type_code()
            effecttypecodes += code_style
        return "{{\\t({},{})}}".format(accel, effecttypecodes)
        pass

    def timer_linear_transform(self, timing: Timing, affectlist: [Affect]):
        # \t{0,5000,\frz3600}Whell
        # Same as above
        # still doing the 10 rotations in 5 seconds.
        if timing is None:
            raise Exception("timing is None")
        effecttypecodes = ""
        for each in affectlist:
            code_style = each.get_affect_type_code()
            effecttypecodes += code_style
        timing_code = "{},{}".format(timing.t0, timing.t1)
        return "{{\\t({},{})}}".format(timing_code, effecttypecodes)

        # \t{0,5000,0.5,\frz3600}Whell
        # Same as above, but it will start fast and slow down,
        # still doing the 10 rotations in 5 seconds.
        pass
        pass

    def timer_non_linear_transform(self, timing: Timing, affectlist: [Affect], accel=0):
        if timing is None:
            raise Exception("timing is None")
        effecttypecodes = ""
        for each in affectlist:
            code_style = each.get_affect_type_code()
            effecttypecodes += code_style
        timing_code = "{},{}".format(timing.t0, timing.t1)
        return "{{\\t({},{},{})}}".format(timing_code, accel, effecttypecodes)

        # \t{0,5000,0.5,\frz3600}Whell
        # Same as above, but it will start fast and slow down,
        # still doing the 10 rotations in 5 seconds.
        pass

    def transform_from_effect_to_effect(self, orgeffect: [],
                                        nexteffect: [Affect],
                                        timing: Timing,
                                        accel=1):
        """
            {\<original effect[list]>\t(new effect[list])}<text>
           {\an5\fscx0\fscy0\t(0,500,\fscx100\fscy100)}Boo!
            Text starts at zero size, i.e. invisible,
            then grows to 100% size in both X and Y direction.
        :return:
        """
        org_type_code = ""
        nex_type_code = ""
        if len(orgeffect) == 0:
            raise Exception("no item in orgeffect")
        for each_effect in orgeffect:
            typecode = each_effect.get_affect_type_code()
            org_type_code += typecode
        if len(nexteffect) == 0:
            raise Exception("no item in nexeffect")
        for each_effect in nexteffect:
            typecode = each_effect.get_affect_type_code()
            nex_type_code += typecode
        if timing is None:
            raise Exception("timing is none")
        timing = '{},{}'.format(timing.t0, timing.t1)
        full_animate_transformation = '{{{}\\t({},{},{})}}'. \
            format(org_type_code,
                   timing,
                   accel,
                   nex_type_code)
        return full_animate_transformation
        pass
