from enum import *

from backend.subeffect.asseffect.AnimatedEffect import AnimatedEffect


class Timing:
    def __init__(self, t0: int, t1: int) -> None:
        super().__init__()
        self.t0 = t0
        self.t1 = t1


class AnimatedTransform:

    def __init__(self) -> None:
        super().__init__()
        self.animationtransform_typecode = '\\t'

    def linear_transform(self, effectlist: [AnimatedEffect.Effect]):
        # linear transform from before /t to after /t animation
        # {\1c&HFF0000&\t(\1c&H0000FF&)}Hello!
        # The text starts out blue,
        # but fades towards red so it is completely red when the line ends.
        effecttypecodes = ""
        for each in effectlist:
            code_style = each.get_effect_type_code()
            effecttypecodes += code_style
        return "\\t{{{}}}".format(effecttypecodes)
        pass

    def non_linear_transform(self, effectlist: [AnimatedEffect.Effect], accel=0):
        # non linear transform from before /t to after /t animation
        # \t{(0.5,\frz3600)}Wheel # transform accel 0.5 (non linear) frz3600
        effecttypecodes = ""
        for each in effectlist:
            code_style = each.get_effect_type_code()
            effecttypecodes += code_style
        return "{{\\t({},{})}}".format(accel, effecttypecodes)
        pass

    def timer_linear_transform(self, timing: Timing, effectlist: [AnimatedEffect.Effect]):
        # \t{0,5000,\frz3600}Whell
        # Same as above
        # still doing the 10 rotations in 5 seconds.
        if timing is None:
            raise Exception("timing is None")
        effecttypecodes = ""
        for each in effectlist:
            code_style = each.get_effect_type_code()
            effecttypecodes += code_style
        timing_code = "{},{}".format(timing.t0, timing.t1)
        return "{{\\t({},{})}}".format(timing_code, effecttypecodes)

        # \t{0,5000,0.5,\frz3600}Whell
        # Same as above, but it will start fast and slow down,
        # still doing the 10 rotations in 5 seconds.
        pass
        pass

    def timer_non_linear_transform(self, timing: Timing, effectlist: [AnimatedEffect.Effect], accel=0):
        if timing is None:
            raise Exception("timing is None")
        effecttypecodes = ""
        for each in effectlist:
            code_style = each.get_effect_type_code()
            effecttypecodes += code_style
        timing_code = "{},{}".format(timing.t0, timing.t1)
        return "{{\\t({},{},{})}}".format(timing_code, accel, effecttypecodes)

        # \t{0,5000,0.5,\frz3600}Whell
        # Same as above, but it will start fast and slow down,
        # still doing the 10 rotations in 5 seconds.
        pass

    def create_animation_transform(self, orgeffect: [AnimatedEffect.Effect],
                                   nexteffect: [AnimatedEffect.Effect],
                                   timing: list,
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
        if timing is not None:
            timing = Timing(timing[0], timing[1])
        else:
            timing = None
        if accel is None:
            accel = 1
        # if len(orgeffect) == 0:
        #     raise Exception("no item in orgeffect")
        if orgeffect is not None:
            for each_effect in orgeffect:
                typecode = each_effect.get_effect_type_code()
                org_type_code += typecode
        # if len(nexteffect) == 0:
        #     raise Exception("no item in nexeffect")
        if nexteffect is not None:
            for each_effect in nexteffect:
                typecode = each_effect.get_effect_type_code()
                nex_type_code += typecode
        if timing is not None:
            timing = '{},{}'.format(timing.t0, timing.t1)
        if timing is None:
            full_animate_transformation = '{{{}\\t({},{})}}'. \
                format(org_type_code,
                       accel,
                       nex_type_code)
        else:
            full_animate_transformation = '{{{}\\t({},{},{})}}'. \
                format(org_type_code,
                       timing,
                       accel,
                       nex_type_code)

        return full_animate_transformation
        pass
