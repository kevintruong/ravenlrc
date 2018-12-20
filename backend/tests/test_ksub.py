import shutil
import unittest

from backend.crawler.asseditor import *
from backend.crawler.subcrawler import *

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

full_test = "https://www.nhaccuatui.com/bai-hat/ngay-chua-giong-bao-nguoi-bat-tu-ost-bui-lan-huong.EoqsR1AFD4SG.html"


class ksub(unittest.TestCase):
    def setUp(self):
        self.testDownloadDir = os.path.join(curDir, "Download")
        if not os.path.isdir(self.testDownloadDir):
            os.mkdir(self.testDownloadDir)

    def tearDown(self):
        shutil.rmtree(self.testDownloadDir)
        pass

    def test_get_sub_from_url(self):
        file = get_sub_file(full_test, self.testDownloadDir)
        self.assertTrue(os.path.isfile(file))

    def test_get_audio_low(self):
        file = download_mp3_file(full_test, self.testDownloadDir, AudioQuanlity.AUDIO_QUANLITY_128)
        self.assertTrue(os.path.isfile(file))

    def test_get_audio_medium(self):
        file = download_mp3_file(full_test, self.testDownloadDir, AudioQuanlity.AUDIO_QUANLITY_320)
        self.assertTrue(os.path.isfile(file))
        pass

    def test_get_audio_lossless(self):
        file = download_mp3_file(full_test, self.testDownloadDir, AudioQuanlity.AUDIO_QUANLITY_LOSSLESS)
        self.assertTrue(os.path.isfile(file))
        pass

    def test_create_ass_sub(self):
        ass_out = os.path.join(self.testDownloadDir, "test.ass")
        newass = create_ass_sub(full_test, ass_out)
        self.assertTrue(os.path.isfile(newass))
        pass


if __name__ == '__main__':
    unittest.main()
