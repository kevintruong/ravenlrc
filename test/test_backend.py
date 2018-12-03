import shutil
import unittest
import os
from click.testing import CliRunner

curDir = os.path.dirname(__file__)
sample_data_dir = os.path.join(curDir, "sample_data")

if not os.path.isdir(sample_data_dir):
    os.mkdir(sample_data_dir)

test_data_dir = os.path.join(sample_data_dir, "test_data")

if os.path.isdir(test_data_dir):
    shutil.rmtree(test_data_dir)
    os.mkdir(test_data_dir)
else:
    os.mkdir(test_data_dir)

input_mp4_file = os.path.join(sample_data_dir, "in1.mp4")
input_mp4_file = input_mp4_file.replace('\\', '\\\\')
bg_img00 = os.path.join(sample_data_dir, "bg_img00.png")
bg_img01 = os.path.join(sample_data_dir, "bg_img01.png")
logo00 = os.path.join(sample_data_dir, "logo00.png")
audio00 = os.path.join(sample_data_dir, "audio01.mp3")

from backendcli import *


class My(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.url = 'https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html'
        pass

    def tearDown(self):
        pass

    def test_click_download_nct(self):
        result = self.runner.invoke(download_content_from_nct,
                                    ["1", self.url, os.path.dirname(__file__)])
        assert result.exit_code == 0
        self.assertTrue(os.path.isfile(get_return_value()))

    def test_click_get_sub_nct(self):
        assfile = os.path.join(os.path.dirname(__file__), "test.ass")
        result = self.runner.invoke(get_sub_nct,
                                    [self.url, assfile, "Arial", "0x018CA7", "--subrect", "150,150,600,200"])
        assert result.exit_code == 0
        self.assertTrue(os.path.isfile(get_return_value()))

    def test_click_add_sub_to_mv(self):
        assfile = os.path.join(os.path.dirname(__file__), "test.ass")
        mvfile = os.path.join(os.path.dirname(__file__), "sample_data\\media_out.mp4")
        result = self.runner.invoke(get_sub_nct,
                                    [self.url, assfile, "UTM Centur", "0x018CA7", "--subrect", "250,180,530,200"])
        assert result.exit_code == 0
        self.assertTrue(os.path.isfile(get_return_value()))

        result = self.runner.invoke(adding_sub_to_mv,
                                    [assfile, mvfile, "output.mp4"])
        assert result.exit_code == 0
        self.assertTrue(os.path.isfile(get_return_value()))

    def test_click_get_media_time_length(self):
        result = self.runner.invoke(get_media_length, [input_mp4_file])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(get_return_value(), str(7))

    if __name__ == '__main__':
        unittest.main()
