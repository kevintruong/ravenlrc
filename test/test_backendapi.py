import os
import shutil
import unittest
import requests

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


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_crawl_lyric(self):
        crawl_cmd = {
            'crawl_type': 'lyric',
            'crawl_url': "nhaccuatuiurl",
            'output': lyric_file  # crawl_tool will store lyric file to output
        }

    def test_build_mv_preview(self):
        build_mv = {
            "type": "preview",
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
            }
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_mv)
        print(response.headers)
        print(response.content)

    def test_build_mv_release(self):
        build_mv = {
            "type": "release",
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
            }
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_mv)
        print(response.headers)
        print(response.content)

    def test_build_template_preview(self):
        build_template = {
            "type": "release",
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
            }
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_template)
        print(response.headers)
        print(response.content)

    def test_build_album(self):
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
            'songlist': [
                {
                    'song': {'song_file': audio00,
                             'song_title': song_title,
                             'song_lyric': lyric_file
                             }
                },
                {
                    'song': {'song_file': audio00,
                             'song_title': song_title,
                             'song_lyric': lyric_file
                             }
                },
                {
                    'song': {'song_file': audio00,
                             'song_title': song_title,
                             'song_lyric': lyric_file
                             }
                },
                {
                    'song': {'song_file': audio00,
                             'song_title': song_title,
                             'song_lyric': lyric_file
                             }
                }
            ]
        }


if __name__ == '__main__':
    unittest.main()
