import unittest
from backend.crawler.asseffect.assaffect import *


class TestAssEffect(unittest.TestCase):

    def test_primary_fill_alpha(self):
        code = AnimationTransform.PrimaryFillShadow(0x20).get_affect_type_code()
        print(code)
        self.assertEqual(code, r'\a&H20&')

    def test_primary_fill_color(self):
        code = AnimationTransform.PrimaryFillColor(0x345678).get_affect_type_code()
        print(code)
        self.assertEqual(code, r'\c&H785634&')


class TestEffectTranformation(unittest.TestCase):
    def test_effect_transformation_effect_to_effect(self):
        # list of org effect
        # list of des effect
        # timing  to transfer form org effect to des effect
        #
        primarycode = AnimationTransform.PrimaryFillColor(0x345678)
        primaryalpha = AnimationTransform.PrimaryFillAlpha(0xAB)
        primarycodedes = AnimationTransform.PrimaryFillColor(0xFFEEFF)
        primaryalphades = AnimationTransform.PrimaryFillAlpha(0xFF)
        animation = AnimationTransform()
        transform_code = animation.transform_from_effect_to_effect([primarycode, primaryalpha],
                                                                   [primarycodedes, primaryalphades],
                                                                   timing=AnimationTransform.Timing(0, 4000), accel=0.4)
        print(transform_code)
        self.assertEqual(transform_code, r'{\c&H785634&\a&Hab&\t(0,4000,0.4,\c&Hffeeff&\a&Hff&)}')
        pass

    def test_timer_non_linear_transform(self):
        # list of org effect
        # list of des effect
        # timing  to transfer form org effect to des effect
        #
        primarycodedes = AnimationTransform.PrimaryFillColor(0xFFEEFF)
        primaryalphades = AnimationTransform.PrimaryFillAlpha(0xFF)
        animation = AnimationTransform()
        transform_code = animation.timer_non_linear_transform(timing=AnimationTransform.Timing(0, 4000),
                                                              affectlist=[primarycodedes, primaryalphades],
                                                              accel=0.4)
        print(transform_code)
        self.assertEqual(transform_code, r'{\t(0,4000,0.4,\c&Hffeeff&\a&Hff&)}')
        pass

    def test_linear_trasnsform(self):
        # list of org effect
        # list of des effect
        # timing  to transfer form org effect to des effect
        #
        primarycodedes = AnimationTransform.PrimaryFillColor(0xFFEEFF)
        primaryalphades = AnimationTransform.PrimaryFillAlpha(0xFF)
        animation = AnimationTransform()
        transform_code = animation.timer_linear_transform(timing=AnimationTransform.Timing(0, 4000),
                                                          affectlist=[primarycodedes, primaryalphades],
                                                          )
        print(transform_code)
        self.assertEqual(transform_code, r'{\t(0,4000,\c&Hffeeff&\a&Hff&)}')
        pass

    def test_non_linear_trasnsform(self):
        # list of org effect
        # list of des effect
        # timing  to transfer form org effect to des effect
        primarycodedes = AnimationTransform.PrimaryFillColor(0xFFEEFF)
        primaryalphades = AnimationTransform.PrimaryFillAlpha(0xFF)
        animation = AnimationTransform()
        transform_code = animation.non_linear_transform(accel=0.4,
                                                        affectlist=[primarycodedes, primaryalphades])
        print(transform_code)
        self.assertEqual(transform_code, r'{\t(0.4,\c&Hffeeff&\a&Hff&)}')
        pass
