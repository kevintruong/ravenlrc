from backend.ffmpeg.ffmpegcli import *
import unittest
import os
import shutil

from backend.subcraw.asseditor import *
from backend.subcraw.subcrawler import download_mp3_file, AudioQuanlity

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
bg_img00 = os.path.join(sample_data_dir, "bg_img00.png")
bg_img01 = os.path.join(sample_data_dir, "bg_img01.png")
logo00 = os.path.join(sample_data_dir, "logo00.png")
audio00 = os.path.join(sample_data_dir, "audio01.mp3")

full_test = "https://www.nhaccuatui.com/bai-hat/ngay-chua-giong-bao-nguoi-bat-tu-ost-bui-lan-huong.EoqsR1AFD4SG.html"
test_url00 = "https://www.nhaccuatui.com/bai-hat/xin-loi-anh-qua-phien-dong-nhi.WX2iJD8VU9ve.html"


class TestFFmpegCli(unittest.TestCase):

    def setUp(self):
        self.ffmpeg = FfmpegCli()
        pass

    def tearDown(self):
        pass

    def test_get_media_time_length(self):
        media_length = self.ffmpeg.get_media_time_length(input_mp4_file)
        self.assertEqual(media_length, 7)
        pass

    def test_add_logo_to_bg_img(self):
        bg_logo_output = os.path.join(test_data_dir, "bg_logo.png")
        self.ffmpeg.add_logo_to_bg_img(bg_img00, logo00, bg_logo_output)
        self.assertTrue(os.path.isfile(bg_logo_output))
        pass

    def test_create_media_file_from_img(self):
        media_output = os.path.join(test_data_dir, "media_out.mp4")
        self.ffmpeg.create_media_file_from_img(bg_img00, 20, media_output)
        length_output = self.ffmpeg.get_media_time_length(media_output)
        self.assertEqual(length_output, 20)

    def test_create_background_affect_with_length(self):
        bg_output = os.path.join(test_data_dir, "bg_out.mp4")
        length_media = 20
        self.ffmpeg.create_background_affect_with_length(input_mp4_file, length_media, bg_output)
        leng_out = self.ffmpeg.get_media_time_length(bg_output)
        self.assertEqual(leng_out, length_media)

    def test_mux_audio_to_video(self):
        output = os.path.join(test_data_dir, "audio_output.mp4")
        self.ffmpeg.mux_audio_to_video(input_mp4_file, audio00, output)
        output_length = self.ffmpeg.get_media_time_length(output)
        input_length = self.ffmpeg.get_media_time_length(input_mp4_file)
        self.assertEqual(output_length, input_length)
        pass

    def test_add_sub_to_video(self):
        media_output = os.path.join(sample_data_dir, "media_out.mp4")
        ass_out = os.path.join(test_data_dir, "test.ass")
        output = os.path.join(test_data_dir, "sub_output.mp4")

        create_ass_sub(full_test, ass_out, sub_rect=SubRectangle(300, 300, 500, 300))
        self.ffmpeg.adding_sub_to_video(ass_out, media_output, output)
        length_in = self.ffmpeg.get_media_time_length(media_output)
        length_out = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(length_out, length_in)
        pass

    def test_add_affect_to_video(self):
        output = os.path.join(test_data_dir, "affect_bg.mp4")
        self.ffmpeg.add_affect_to_video(input_mp4_file, input_mp4_file, output)
        inputLeng = self.ffmpeg.get_media_time_length(input_mp4_file)
        outputLeng = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(outputLeng, inputLeng)
        pass

    def create_mv_from_url(self, url: str):
        bg_mv = os.path.join(test_data_dir, "bg_mv.mp4")
        bg_img = os.path.join(test_data_dir, "bg_img_abc.png")
        ass_out = os.path.join(test_data_dir, "test.ass")
        output = os.path.join(test_data_dir, "sub_output.mp4")
        final_mv = os.path.join(test_data_dir, "final_mv.mp4")

        # download mp3 file
        self.ffmpeg.set_resolution(FFmpegProfile.PROFILE_LOW)
        audiofile = download_mp3_file(url, test_data_dir, AudioQuanlity.AUDIO_QUANLITY_320)
        audio_length = self.ffmpeg.get_media_time_length(audiofile)
        self.ffmpeg.add_logo_to_bg_img(bg_img00, logo00, bg_img)
        self.ffmpeg.create_media_file_from_img(bg_img, audio_length, bg_mv)
        # add sub to MV
        create_ass_sub(url, ass_out, resolution=[640, 480])  # get sub
        self.ffmpeg.adding_sub_to_video(ass_out, bg_mv, output)
        # add audio to MV
        self.ffmpeg.mux_audio_to_video(output, audiofile, final_mv)
        final_length = self.ffmpeg.get_media_time_length(final_mv)
        self.assertEqual(final_length, audio_length)

    def test_full_create_mv(self):
        # self.create_mv_from_url(full_test)
        self.create_mv_from_url(test_url00)


if __name__ == '__main__':
    unittest.main()
