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

        pass
