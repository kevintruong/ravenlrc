import os
import shutil
import unittest
import requests
from backend.TempFileMnger import *

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
affect_file = os.path.join(sample_data_dir, "affect_file.mp4")
titlefile = os.path.join(sample_data_dir, "Xinloi.png")
lyric_file = os.path.join(sample_data_dir, "xinloi.lrc")
nct_url = "https://www.nhaccuatui.com/bai-hat/ngay-chua-giong-bao-nguoi-bat-tu-ost-bui-lan-huong.EoqsR1AFD4SG.html"


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_crawl_lyric(self):
        lyric = LrcTempFile().getfullpath()
        crawl_cmd = {
            'crawl_type': 0,
            'crawl_url': nct_url,
            'output': lyric  # crawl_tool will store lyric file to output
        }
        response = requests.post('http://localhost:8000/crawl',
                                 json=crawl_cmd)
        print(response.headers)
        print(response.content)
        self.assertTrue(os.path.isfile(lyric))

    def test_crawl_song(self):
        crawl_cmd = {
            'crawl_type': 1,
            'crawl_url': "nhaccuatuiurl",
            'audio_quality': 1,
            'output': audio00  # crawl_tool will store lyric file to output
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=crawl_cmd)
        print(response.headers)
        print(response.content)

    def test_crawl_song_lyric(self):
        crawl_cmd = {
            'crawl_type': 2,
            'crawl_url': "nhaccuatuiurl",
            'audio_quality': 1,
            'output_lrc': audio00,  # crawl_tool will store lyric file to output
            'output_audio': lyric_file
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=crawl_cmd)
        print(response.headers)
        print(response.content)

    def test_build_mv_preview(self):
        build_template = {
            "type": 0,
            "song_info": {
                "song_file": audio00,
                "lyric_file": lyric_file,
                "song_name": "Nhắm mắt thấy mùa hè"
            },
            "background_inf": {
                "bg_file": bg_img00,
                "sub_info": {
                    'coordinate': [100, 100],
                    'size': [200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20
                }
            },
            "affect_inf": {
                'affect_file': affect_file,
                'opacity': 50
            },
            'output': os.path.join(test_data_dir, 'preview_template.mp4')
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_template)
        print(response.headers)
        print(response.content)

    def test_build_mv_release(self):
        build_mv = {
            "type": 1,
            "song_info": {
                "song_file": audio00,
                "lyric_file": lyric_file,
                "song_name": "Nhắm mắt thấy mùa hè",
                "title_file": titlefile
            },
            "background_info": {
                "bg_file": bg_img00,
                "sub_info": {
                    'rectangle': [100, 100, 200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20
                },
                "title_info": {
                    'rectangle': [100, 100, 0, 0],  # must has
                    'fontname': 'UTM Centur',  # Can be None
                    'fontcolor': 0x018CA7,  # Can be None
                    'fontsize': 20  # Can be None
                }
            },
            "affect_info": {
                'affect_file': affect_file,
                'opacity': 50
            }
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_mv)
        print(response.headers)
        print(response.content)

    def test_build_template_preview(self):
        build_template = {
            "type": 0,
            "background_inf": {
                "bg_file": bg_img00,
                "sub_info": {
                    'coordinate': [100, 100],
                    'size': [200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20
                }
            },
            "affect_inf": {
                'affect_file': affect_file,
                'opacity': 50
            },
            'output': os.path.join(test_data_dir, 'preview_template.mp4')
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_template)
        print(response.headers)
        print(response.content)

    def test_build_template_release(self):
        build_template = {
            "type": 1,
            "background_inf": {
                "bg_file": bg_img00,
                "sub_info": {
                    'coordinate': [100, 100],
                    'size': [200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20
                }
            },
            "affect_inf": {
                'affect_file': affect_file,
                'opacity': 50
            },
            'output': os.path.join(test_data_dir, 'release_template.mp4')
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_template)
        print(response.headers)
        print(response.content)

    def test_build_album(self):
        """
        TODO build a json request for create MV from a list of song

        :rtype: object
        """
        song_title = None
        build_album = {
            "album_title": "Name of album",
            "background_inf": {
                "bg_file": bg_img00,
                "sub_info": {
                    'coordinate': [100, 100],
                    'size': [200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20
                }
            },
            "songlist": [
                {
                    'song_inf': {'song_file': audio00,
                                 'song_title': song_title,
                                 'song_lyric': lyric_file
                                 }
                },
                {
                    'song_info': {'song_file': audio00,
                                  'song_title': song_title,
                                  'song_lyric': lyric_file
                                  }
                },
                {
                    'song_info': {'song_file': audio00,
                                  'song_title': song_title,
                                  'song_lyric': lyric_file
                                  }
                },
                {
                    'song_info': {'song_file': audio00,
                                  'song_title': song_title,
                                  'song_lyric': lyric_file
                                  }
                }
            ],
            'output': os.path.join(test_data_dir, 'album_mv.mp4')
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_album)
        print(response.headers)
        print(response.content)


if __name__ == '__main__':
    unittest.main()
