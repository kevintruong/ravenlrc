import unittest

from backend.crawler.asseditor import SubtitleInfo
from backend.crawler.keyword.keyword import *
from backend.ffmpeg.ffmpegcli import FfmpegCli

from backend.crawler.asseffect.AnimatedAffect import AnimatedAffect


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
        self.keywork_config = {
            'fontname': 'UTMAmericanaItalic',
            'fontsize': 30,
            'fontcolor': 0x028CF7,
            'alignment': SubtitleAlignment.SUB_ALIGN_RIGHT_JUSTIFIED
        }

    def process_ass_with_effect(self, effectconf_dict: dict):
        configure_dict = effectconf_dict
        self.formatter = AssDialogueTextKeyWordFormatter(self.keywork_config)

        self.textprocessor = AssDialogueTextProcessor(keyword=self.keywork,
                                                      formatter=self.keywork_config,
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
        ass_out = r'D:\Project\ytcreatorservice\backend\crawler\test\newtest.ass'
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
            'effect_start': [AnimatedAffect.FontSize(20)],
            'effect_transform': [AnimatedAffect.FontSize(40)],
            'timing': [0, 5000],
            'accel': 0.3
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_zoom_out(self):
        configure_dict = {
            'effect_start': [AnimatedAffect.FontSize(50),
                             AnimatedAffect.BlurEdgesGaussian(2)],

            'effect_transform': [AnimatedAffect.FontSize(10),
                                 AnimatedAffect.BlurEdgesGaussian(20)],
            'timing': [0, 5000],
            'accel': 0.8
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_border_increase(self):
        configure_dict = {
            'effect_start': [AnimatedAffect.ShadowDistanceX(50),
                             AnimatedAffect.ShadowDistanceY(50)],
            'effect_transform': [AnimatedAffect.ShadowDistanceX(0),
                                 AnimatedAffect.ShadowDistanceY(0)],
            'timing': [0, 5000],
            'accel': 0.8
        }
        self.process_ass_with_effect(configure_dict)

    def test_processkeyword_effect_text_rotate(self):
        # TODO
        # \t{0,5000,\frz3600}Whell
        configure_dict = {
            'effect_transform': [],
            'timing': [0, 5000],
            'accel': 0.8
        }
        self.process_ass_with_effect(configure_dict)


class testAssDialueTextAnimatedTransform(unittest.TestCase):
    def setUp(self):
        configure_dict = {
            'effect_start': [AnimatedAffect.FontSize(10),
                             AnimatedAffect.PrimaryFillColor(0xff0000)],
            'effect_transform': [AnimatedAffect.FontSize(30),
                                 AnimatedAffect.PrimaryFillColor(0xffeeff)],
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
