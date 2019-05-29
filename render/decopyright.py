from backend.utility.TempFileMnger import MvTempFile, PngTempFile
from render.ffmpegcli import FfmpegCli


class DeCopyright:
    def __init__(self, mediafile, width, height):
        self.media_file = mediafile
        self.width = width
        self.height = height

    def run(self, output):
        FfmpegCli().decopyright_video(self.media_file, output, self.width, self.height)
        pass


import unittest


class test_decopyright(unittest.TestCase):
    def setUp(self) -> None:
        self.mediafile = '/home/kevin/Downloads/03f20b9a046b96eff1928f7319a65022.mp4'
        self.decopyright = DeCopyright(self.mediafile)

    def test_decopyright(self):
        tempfile = '/tmp/raven/test1.mp4'
        self.decopyright.run(tempfile)
        # FfmpegCli().create_noise_color_input(0xaabbcc,tempfile)
