import unittest

from backend.subeffect.asseditor import SubtitleInfo, create_ass_from_lrc
from backend.subeffect.asseffect.LyricEffect import LyricEffect
from backend.subeffect.asseffect.LyricEffect import KeyWordInfo
from backend.subeffect.keyword.keyword import *
from backend.render.ffmpegcli import FfmpegCli, FFmpegProfile

from backend.subeffect.asseffect.AnimatedEffect import AnimatedEffect


class TestKeyword(unittest.TestCase):

    def test_dialogTextStyleCode_create_fontname(self):
        fontname_codestyle = DialogueTextStyleCode.create_fontname_style_code('Arial')
        print(fontname_codestyle)
        self.assertEqual(fontname_codestyle, r"{\fnArial}")

    def test_dialogTextStyleCode_create_fontsize(self):
        fontsize = 20
        fontsize_codestyle = DialogueTextStyleCode.create_fontsize_style_code(fontsize)
        print(fontsize_codestyle)
        self.assertEqual(fontsize_codestyle, r"{\fs20}")

    def test_dialogTextSytleCode_create_fontcolor(self):
        fontcolor = 0x123456  # font color in rgb
        fontcolor_stylecode = DialogueTextStyleCode.create_fontcolor_style_code(fontcolor)
        print(fontcolor_stylecode)
        self.assertEqual(fontcolor_stylecode, r"{\c&563412&}")


class testKeywordFormatter(unittest.TestCase):

    def setUp(self):
        super().setUp()
        keywork_config = {
            'fontname': 'UTM Centur',
            'fontsize': 20,
            'fontcolor': 0x018CA7,
            'alignment': SubtitleAlignment.SUB_ALIGN_RIGHT_JUSTIFIED
        }
        animation_conf = {

        }
        self.formatter = AssDialogueTextKeyWordFormatter(keywork_config)

    def test_formatkeyword(self):
        formatted_keyword = self.formatter.format_keyword("Yêu anh")
        print(formatted_keyword)
        self.assertEqual(formatted_keyword, r'{\fnUTM Centur}{\fs20}{\c&7ca18&}{\a3}Yêu anh')


class testAssDialogueTextProcessor(unittest.TestCase):

    def setUp(self):
        self.keywork = ['khung hình',
                        'một ngày',
                        'gặp lại',
                        'nỗi đau',
                        'thương',
                        'an yên',
                        'mây ngàn',
                        'thương anh',
                        'Nơi xa',
                        'Ngày mai', 'gió', 'thấy', 'gặp nhau', 'sống',
                        'nắng', 'biến mất', 'hoa tàn',
                        'Dòng thư',
                        'giấc mơ',
                        'Bên nhau',
                        'xa nhau',
                        'ký ức',
                        'những nhiệm màu',
                        'quên',
                        'nhớ',
                        ]
        super().setUp()
        self.ass_lyric = open('test.ass', 'r', encoding='utf-8')
        self.keyword_formatter = {
            'fontname': 'UTMAmericanaItalic',
            'fontsize': 30,
            'fontcolor': 0x028CF7,
            'alignment': SubtitleAlignment.SUB_ALIGN_RIGHT_JUSTIFIED
        }

    def process_ass_with_effect(self, effectconf_dict: dict):
        configure_dict = effectconf_dict
        self.formatter = AssDialogueTextKeyWordFormatter(self.keyword_formatter)

        self.textprocessor = AssDialogueTextProcessor(keyword=self.keywork,
                                                      formatter=self.keyword_formatter,
                                                      animatedconf=configure_dict)

        content = self.ass_lyric.read()
        content = self.textprocessor.keyword_process(content)
        with open('newtest.ass', 'w', encoding='utf-8') as filewr:
            filewr.write(content)
        print(content)
        self.run_ffmpeg_mux_sub()

    def run_ffmpeg_mux_sub(self):
        self.ffmpeg = FfmpegCli()
        media_output = "audio_output.mp4"
        ass_out = 'newtest.ass'
        output = "sub_output.mp4"

        subinfo = SubtitleInfo({'rectangle': [100, 100, 600, 400],
                                'fontname': 'UTM Centur',
                                'fontcolor': 0x018CA7,
                                'fontsize': 40})
        # create_ass_sub(full_test, ass_out, subinfo)

        self.ffmpeg.adding_sub_to_video(ass_out, media_output, output)
        length_in = self.ffmpeg.get_media_time_length(media_output)
        length_out = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(length_out, length_in)
        pass

    def test_processkeyword_effect_zoom_in(self):
        configure_dict = {
            'effect_start': [AnimatedEffect.FontSize(20)],
            'effect_transform': [AnimatedEffect.FontSize(40)],
            'timing': [0, 5000],
            'accel': 0.3
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_zoom_out(self):
        configure_dict = {
            'effect_start': [AnimatedEffect.FontSize(50),
                             AnimatedEffect.BlurEdgesGaussian(2)],

            'effect_transform': [AnimatedEffect.FontSize(10),
                                 AnimatedEffect.BlurEdgesGaussian(20)],
            'timing': [0, 5000],
            'accel': 0.8
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_border_increase(self):
        configure_dict = {
            'effect_start': [AnimatedEffect.Border(50)],
            'effect_transform': [AnimatedEffect.Border(0)],
            'timing': [0, 5000],
            'accel': 1
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_text_rotate_X(self):
        # \t{0,5000,\frz3600}Whell
        configure_dict = {'effect_start': [AnimatedEffect.PrimaryFillColor(0xABFFCD),
                                           AnimatedEffect.FontSize(20)],
                          'effect_transform': [AnimatedEffect.PrimaryFillColor(0x123456),
                                               AnimatedEffect.FontSize(40),
                                               AnimatedEffect.TextRotationX(360 * 3)],
                          'timing': [0, 6000],
                          'accel': 0.8
                          }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_text_rotate_Y(self):
        # \t{0,5000,\frz3600}Whell
        configure_dict = {'effect_start': [AnimatedEffect.PrimaryFillColor(0xABFFCD),
                                           AnimatedEffect.FontSize(20)],
                          'effect_transform': [AnimatedEffect.PrimaryFillColor(0x123456),
                                               AnimatedEffect.FontSize(40),
                                               AnimatedEffect.TextRotationY(360 * 3)],
                          'timing': [0, 6000],
                          'accel': 0.8
                          }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_text_rotate_Z(self):
        # \t{0,5000,\frz3600}Whell
        configure_dict = {'effect_start': [AnimatedEffect.PrimaryFillColor(0xABFFCD),
                                           AnimatedEffect.FontSize(20)],
                          'effect_transform': [AnimatedEffect.PrimaryFillColor(0x123456),
                                               AnimatedEffect.FontSize(40),
                                               AnimatedEffect.TextRotationZ(60)],
                          'timing': [0, 6000],
                          'accel': 0.8
                          }
        self.process_ass_with_effect(configure_dict)

    def test_animated_effect_text_shearing(self):
        configure_dict = {'effect_start': [AnimatedEffect.PrimaryFillColor(0xABFFCD),
                                           AnimatedEffect.FontSize(20)],
                          'effect_transform': [AnimatedEffect.PrimaryFillColor(0x123456),
                                               AnimatedEffect.FontSize(40),
                                               AnimatedEffect.TextShearingX(1),
                                               AnimatedEffect.TextShearingY(0.5)],
                          'timing': [0, 6000],
                          'accel': 0.8
                          }
        self.process_ass_with_effect(configure_dict)


class testAssDialueTextAnimatedTransform(unittest.TestCase):
    def setUp(self):
        configure_dict = {
            'effect_start': [AnimatedEffect.FontSize(10),
                             AnimatedEffect.PrimaryFillColor(0xff0000)],
            'effect_transform': [AnimatedEffect.FontSize(30),
                                 AnimatedEffect.PrimaryFillColor(0xffeeff)],
            'timing': [0, 5000],
            'accel': 0.3
        }
        self.assdialogueanimatedtransform = AssDialueTextAnimatedTransform(configure_dict)

    def test_create_full_transfer(self):
        fulltransfer = self.assdialogueanimatedtransform.create_full_transform()
        print(fulltransfer)
        self.assertEqual(fulltransfer, r'{\fs10\c&H0000ff&\t(0,5000,0.3,\fs50\c&Hffeeff&)}')
        if __name__ == '__main__':
            unittest.main()


import unittest


class test_effectinfo(unittest.TestCase):
    def test_init(self):
        effect_info = {
            # Zoom in and change keyword color format
            'effect_start': [[1,  # font size code
                              20],  # font size is 20
                             [2,  # font color code
                              0x345678  # font color hex code
                              ]],
            'transform_effect': [[1, 50],
                                 [2, 0xffeeff]],
            'timing': "",  # timing is None mean mean duration = duration sub line
            'accel': 0.8
        }
        effect_info_dict = AssDialueTextAnimatedTransform.json2dict(effect_info)
        effctinfo = AssDialueTextAnimatedTransform(effect_info_dict)
        effect = effctinfo.create_full_transform()
        print("hello {}", format(effect))


class test_LyricEffect(unittest.TestCase):
    def setUp(self):
        self.keywork = ['khung hình',
                        'một ngày',
                        'gặp lại',
                        'nỗi đau',
                        'thương',
                        'an yên',
                        'mây ngàn',
                        'thương anh',
                        'Nơi xa',
                        'Ngày mai', 'gió', 'thấy', 'gặp nhau', 'sống',
                        'nắng', 'biến mất', 'hoa tàn',
                        'Dòng thư',
                        'giấc mơ',
                        'Bên nhau',
                        'xa nhau',
                        'ký ức',
                        'những nhiệm màu',
                        'quên',
                        'nhớ',
                        ]
        lyric_effect = {  # can be None
            'effect_type': 1,  # animation effect_code
            'keyword_info': {
                'keywords': self.keywork,  # Keyword for subtitle effect, can be None.
                # if keywork is none => effect bellow apply for whole lyric
                'keyword_fmt': {
                    'fontname': 'UTMAmericanaItalic',
                    'fontsize': 30,
                    'fontcolor': 0x028CF7,
                    'alignment': 3
                }
            },
            'effect_info': {
                # Zoom in and change keyword color format
                'effect_start': [[1,  # font size code
                                  20],  # font size is 20
                                 [2,  # font color code
                                  0x345678  # font color hex code
                                  ]],
                'effect_transform': [[1, 50],
                                     [2, 0xffeeff]],
                'timing': "",  # timing is None mean mean duration = duration sub line
                'accel': 0.8
            }
        }
        self.lyriceffect = LyricEffect(lyric_effect)

    def test_apply_lyric_effect(self):
        subinfo = {
            'rectangle': [100, 100, 200, 300],
            'fontname': 'UTM Centur',
            'fontcolor': 0x018CA7,
            'fontsize': 20,
        }
        subcustomizer = create_ass_from_lrc(
            r'D:\Project\ytcreatorservice\backend\crawler\test\Nhắm Mắt Thấy Mùa Hè (Nhắm Mắt Thấy Mùa Hè OST).lrc',
            'test.ass', subinfo=SubtitleInfo(subinfo),
            resolution=FFmpegProfile.PROFILE_FULLHD.value)
        for line in subcustomizer.subs:
            print(line.text)
            line.text = self.lyriceffect.apply_lyric_effect(line.text, line.duration)
            print(line.text)
        subcustomizer.subs.save("lyric_effect_test.ass")

        pass
