import unittest
from backend.crawler.keyword.keyword import *


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
                        'mây ngàn']
        super().setUp()
        self.ass_lyric = open('test.ass', 'r', encoding='utf-8')
        keywork_config = {
            'fontname': 'UTM Scriptina KT',
            'fontsize': 80,
            'fontcolor': 0x028CF7,
            'alignment': SubtitleAlignment.SUB_ALIGN_RIGHT_JUSTIFIED
        }
        configure_dict = {
            'effect_start': [FontSize(10), PrimaryFillColor(0xff0000)],
            'effect_transform': [FontSize(50), PrimaryFillColor(0xffeeff)],
            'timing': [0, 5000],
            'accel': 0.3
        }
        self.formatter = AssDialogueTextKeyWordFormatter(keywork_config)

        self.textprocessor = AssDialogueTextProcessor(keyword=self.keywork,
                                                      formater=keywork_config,
                                                      animatedconf=configure_dict)

    def test_processkeyword(self):
        content = self.ass_lyric.read()
        content = self.textprocessor.keyword_process(content)
        with open('newtest.ass', 'w', encoding='utf-8') as filewr:
            filewr.write(content)
        print(content)



class testAssDialueTextAnimatedTransform(unittest.TestCase):
    def setUp(self):
        configure_dict = {
            'effect_start': [FontSize(10), PrimaryFillColor(0xff0000)],
            'effect_transform': [FontSize(50), PrimaryFillColor(0xffeeff)],
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
