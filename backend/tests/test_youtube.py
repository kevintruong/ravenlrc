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
        publishtime = datetime.datetime.now() + datetime.timedelta(days=3)
        publish_at = publishtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(publish_at)
        status = YtMvConfigStatus(publishAt=publish_at)
        snippet = YtMvConfigSnippet("[Phạm Hoài Nam][Lyric] Mong Manh",
                                    "this is the description",
                                    10,
                                    'phamhoainam,mongmanh')
        id = self.uploader.upload_video(
            r'D:\Project\ytcreatorservice\backend\content\Mv\Release\build_release_Mong Manh.mp4',
            snippet, status)
        # id = self.uploader.upload_video(
        #     r'D:\Project\ytcreatorservice\backend\content\Mv\Release\build_release_Em À.mp4')

        info = self.uploader.get_video_info_by_id(id)
        self.assertEqual(info['title'], self.uploader.get_title())
        info = self.uploader.get_video_info_by_id(id)
        self.assertEqual(info['title'], self.uploader.get_title())

    def test_get_video_info(self):
        id = '5h7m7PXPbvc'
        info = self.uploader.get_video_info_by_id(id)
        print(json.dumps(info, indent=True))
        self.assertEqual(info['title'], self.uploader.get_title())

    def test_update_video_to_chanel(self):
        self.assertEqual(True, False)

    def test_remove_video_by_id(self):
        self.uploader.remove_video_by_id('Rhv7_5cK6DM')

    def test_update_video_by_id(self):
        id = 'N4xvInoKuwI'
        publishtime = datetime.datetime.now() + datetime.timedelta(days=3)
        publish_at = publishtime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(publish_at)

        status = YtMvConfigStatus(publishAt=publish_at)
        # status = YtMvConfigStatus(publishAt=r'2019-01-25T02:01:07.000Z')
        snippet = YtMvConfigSnippet("[Hà Anh Tuấn][Lyric] Em à",
                                    "this is the description",
                                    10,
                                    'haanhtuan,ema')
        print(json.dumps(status.to_dict(), indent=True))
        # status = {"privacyStatus": "private",
        #           "publishAt": "2019-01-27T17:00:00.000Z"}
        # print(json.dumps(status, indent=True))

        rsp = self.uploader.update_video_by_id(id, snippet.to_dict(), status.to_dict())
        print(rsp)


if __name__ == '__main__':
    unittest.main()
