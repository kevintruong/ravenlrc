import os
import shutil
import unittest

from backend.subeffect.asseditor import LyricConfigInfo, create_ass_from_url
from backend.render.ffmpegcli import FfmpegCli
from backend.utility.TempFileMnger import *

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

full_test = "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html"
test_url00 = "https://www.nhaccuatui.com/bai-hat/xin-loi-anh-qua-phien-dong-nhi.WX2iJD8VU9ve.html"


class TestFFmpegCli(unittest.TestCase):

    def setUp(self):
        self.ffmpeg = FfmpegCli()
        pass

    def test_create_media_file_from_img(self):
        media_output = os.path.join(sample_data_dir, "media_out.mp4")
        timelength = int(self.ffmpeg.get_media_time_length(audio00) / 6)

        self.ffmpeg.create_media_file_from_img(bg_img00, timelength, media_output)
        length_output = self.ffmpeg.get_media_time_length(media_output)
        self.assertEqual(length_output, timelength)
        output = os.path.join(sample_data_dir, "audio_output.mp4")

        self.ffmpeg.mux_audio_to_video(media_output, audio00, output)

        output_length = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(output_length, timelength)
        pass

    def test_add_sub_to_video(self):
        media_output = os.path.join(sample_data_dir, "audio_output.mp4")
        ass_out = AssTempFile().getfullpath()
        output = os.path.join(sample_data_dir, "sub_output.mp4")

        subinfo = LyricConfigInfo({'rectangle': [100, 100, 600, 400],
                                'fontname': 'UTM Centur',
                                'fontcolor': 0x018CA7,
                                'fontsize': 40})
        create_ass_from_url(full_test, ass_out, subinfo)

        self.ffmpeg.adding_sub_to_video(ass_out, media_output, output)
        length_in = self.ffmpeg.get_media_time_length(media_output)
        length_out = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(length_out, length_in)
        pass

    def test_add_sub_to_video_lyric_effect(self):
        media_output = os.path.join(sample_data_dir, "audio_output.mp4")
        ass_out = AssTempFile().getfullpath()
        output = os.path.join(sample_data_dir, "sub_output.mp4")

        subinfo = LyricConfigInfo({'rectangle': [100, 100, 600, 400],
                                'fontname': 'UTM Centur',
                                'fontcolor': 0x018CA7,
                                'fontsize': 40})
        create_ass_from_url(full_test, ass_out, subinfo)

        self.ffmpeg.adding_sub_to_video(r'D:\Project\ytcreatorservice\backend\subeffect\test\lyric_effect_test.ass',
                                        media_output,
                                        output)
        length_in = self.ffmpeg.get_media_time_length(media_output)
        length_out = self.ffmpeg.get_media_time_length(output)
        self.assertEqual(length_out, length_in)
