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
        self.textprocessor = AssDialogueTextProcessor(keyword=self.keywork)
        self.ass_lyric = open('test.ass', 'r', encoding='utf-8')
        keywork_config = {
            'fontname': 'UTM Scriptina KT',
            'fontsize': 80,
            'fontcolor': 0x028CF7,
            'alignment': SubtitleAlignment.SUB_ALIGN_RIGHT_JUSTIFIED
        }
        self.formatter = AssDialogueTextKeyWordFormatter(keywork_config)

    def test_processkeyword(self):
        replace_keyword = []
        content = self.ass_lyric.read()
        for each_keyword in self.keywork:
            replaceword = self.formatter.format_keyword(each_keyword)
            replace_keyword.append(replaceword)
            self.textprocessor.kwprocessor.add_keyword(each_keyword, replaceword)
            content = self.textprocessor.kwprocessor.replace_keywords(content)
            self.textprocessor.kwprocessor.remove_keyword(each_keyword)
            self.textprocessor.kwprocessor.remove_keyword(replaceword)
        with open('newtest.ass', 'w', encoding='utf-8') as filewr:
            filewr.write(content)
        print(content)


if __name__ == '__main__':
    unittest.main()
