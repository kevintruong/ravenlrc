import os

# from pysubs2 import SSAFile, SSAEvent
from backend.vendor.pysubs2 import SSAFile, SSAEvent
from render.ffmpegcli import FfmpegCli

CurDir = os.path.dirname(os.path.realpath(__file__))
TemplateDir = os.path.join(CurDir, 'template')


class HeaderFooter:
    headerfooterass_file = os.path.join(TemplateDir, 'header_footer.ass')

    def __init__(self, header=None, footer=None, videofile=None):
        self.header = header
        self.footer = footer
        self.videofile = videofile
        self.timelength = int(FfmpegCli().get_media_time_length(self.videofile) * 1000)
        if not os.path.exists(self.headerfooterass_file):
            raise FileExistsError('header_footer.ass file not exist')

    def generate_header_footer_subtitle(self, outputfile):
        subs = SSAFile.load(self.headerfooterass_file, encoding='utf-8')
        if self.header:
            event = SSAEvent()
            event.start = 0
            event.end = self.timelength
            event.style = 'header'
            event.text = self.header
            subs.events.append(event)
        if self.footer:
            event = SSAEvent()
            event.start = 0
            event.end = self.timelength
            event.style = 'footer'
            event.text = self.footer
            subs.events.append(event)
        subs.save(outputfile)
        return outputfile


import unittest


class TestHeaderFooter(unittest.TestCase):
    def setUp(self) -> None:
        self.videofile = '/mnt/Data/Project/ytcreatorservice/test/sample_data/affect_file.mp4'
        self.headerfooter = HeaderFooter('hello kevin header', 'this is my footer', videofile=self.videofile)

    def test_generate_header_footer_ass(self):
        videofile = self.headerfooter.generate_header_footer_subtitle('/tmp/test.ass')
        if videofile:
            with open(videofile, 'r') as assfile:
                data = assfile.read()
                print(data)
        pass
