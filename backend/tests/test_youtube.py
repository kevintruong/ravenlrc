from backend.publisher.fb_publish import FbPageAPI

test_dir = os.path.dirname(__file__)
sample_data = os.path.join(test_dir, "sample_data")

test_video = os.path.join(sample_data, "in1.mp4")


class TestYoutubeChanelAPI(unittest.TestCase):

    def setUp(self):
        self.uploader = YoutubeUploader('timshel')
        pass

    def tearDown(self):
        pass

    def test_login(self):
        self.assertEqual(True, False)

    def test_logout(self):
        self.assertEqual(True, False)

    def test_upload_video_to_channel(self):
        status = YtMvConfigStatus(5)
        snippet = YtMvConfigSnippet.create_snippet_from_info(YoutubeMVInfo('timshel', 'mong manh'))
        id = self.uploader.upload_video(
            r'D:\Project\ytcreatorservice\backend\content\Mv\Release\build_release_Mong Manh.mp4',
            snippet, status)

        info = self.uploader.get_video_info_by_id(id)
        self.assertEqual(info['title'], snippet.title)
        info = self.uploader.get_video_info_by_id(id)
        self.assertEqual(info['title'], snippet.title)

    def test_get_video_info(self):
        id = '5R1YpuxwsN0'
        info = self.uploader.get_video_info_by_id(id)
        tags = ','.join(info['snippet']['tags'])
        description = tags + '\n' + info['snippet']['description']
        link = "https://www.youtube.com/watch?v={}".format(id)
        fbpage = FbPageAPI('timshel')
        fbpage.post(message=description, link=link)

    def test_update_video_to_chanel(self):
        self.assertEqual(True, False)

    def test_remove_video_by_id(self):
        self.uploader.remove_video_by_id('Rhv7_5cK6DM')

    def test_update_video_by_id(self):
        id = 'Xzpyz7ieDqo'
        status = YtMvConfigStatus(5)
        mvinfo = YoutubeMVInfo('timshel', 'hay ra khoi nguoi do')
        snippet = YtMvConfigSnippet.create_snippet_from_info(mvinfo)
        print(json.dumps(status.to_dict(), indent=True))
        rsp = self.uploader.update_video_by_id(id, snippet, None)
        print(rsp)


if __name__ == '__main__':
    unittest.main()
