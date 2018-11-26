import unittest
from backend.youtube.youtube_uploader import *

test_dir = os.path.dirname(__file__)
sample_data = os.path.join(test_dir, "sample_data")

test_video = os.path.join(sample_data, "in1.mp4")


class TestYoutubeChanelAPI(unittest.TestCase):

    def setUp(self):
        self.uploader = YoutubeUploader("Test google uploader", "this is my test kevinelg",
                                        ['googleapi', 'timshel'], 24)
        pass

    def tearDown(self):
        pass

    def test_login(self):
        self.assertEqual(True, False)

    def test_logout(self):
        self.assertEqual(True, False)

    def test_upload_video_to_channel(self):
        id = self.uploader.upload_video(test_video)
        info = self.uploader.get_video_info_by_id(id)
        self.assertEqual(info['title', self.uploader.get_title()])

    def test_get_video_info(self):
        info = self.uploader.get_video_info_by_id("u2958BANJu0")
        self.assertEqual(info['title'], self.uploader.get_title())

    def test_update_video_to_chanel(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
