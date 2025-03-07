import json
import shutil
import unittest

import requests

from Api.publish import publish_vid
from render.engine import MvSongRender
from render.parser import SongApi
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
input_mp4_file = input_mp4_file.replace('\\', '\\\\')
bg_img00 = os.path.join(sample_data_dir, "bg_img00.png")
bg_img01 = os.path.join(sample_data_dir, "bg_img01.png")
logo00 = os.path.join(sample_data_dir, "logo00.png")
audio00 = os.path.join(sample_data_dir, "audio01.mp3")
ngaychuagiongbao_audiofile = os.path.join(sample_data_dir, "NgayChuaGiongBaoNguoiBatTuOst-BuiLanHuong-5708274_hq.mp3")
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
            'crawl_url': nct_url,
            'output': test_data_dir
        }
        response = requests.post('http://localhost:8000/crawl',
                                 json=crawl_cmd).json()
        jsondata = json.loads(response)
        print(jsondata)
        self.assertTrue(os.path.isfile(lyric))

    def test_build_mv_preview(self):
        build_template = {
            "type": 0,
            "song_info": {
                {
                    'localtion': r'/tmp/ytcreator/test/sample_data/test_data/Ngày Chưa Giông Bão (Người Bất Tử '
                                 r'OST)_Bùi Lan Hương.mp3',
                    'lyric': r'/tmp/ytcreator/test/sample_data/test_data/Ngày Chưa Giông Bão (Người Bất Tử OST).lrc',
                    'singerTitle': 'Bùi Lan Hương',
                    'songurl': r'https://m.nhaccuatui.com/bai-hat/ngay-chua-giong-bao-nguoi-bat-tu-ost-bui-lan-huong'
                               r'.EoqsR1AFD4SG.html',
                    'title': 'Ngày Chưa Giông Bão (Người Bất Tử OST)'},
            },
            "background_info": {
                "bg_file": bg_img00,
                "sub_info": {
                    'rectangle': [100, 100, 200, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 20,
                },
                "title_info": {
                    'rectangle': [100, 100, 0, 0],  # must has
                    'fontname': 'UTM Centur',  # Can be None
                    'fontcolor': 0x018CA7,  # Can be None
                    'fontsize': 20,  # Can be None

                }
            },
            "effect_info": {
                'affect_file': affect_file,
                'opacity': 50
            },
            'lyric_effect': {  # can be None
                'effect_type': 1,  # animation effect_code
                'keyword_info': {
                    'keywords': ['hello'],  # Keyword for subtitle effect, can be None.
                    # if keywork is none => effect bellow apply for whole lyric
                    'keyword_fmt': {
                        'fontname': 'UTMAmericanaItalic',
                        'fontsize': 30,
                        'fontcolor': 0x028CF7,
                        'alignment': 3
                    }
                },
                'effect_info': {
                    # Zoom in and change keyword color format
                    'effect_start': [[1,  # font size code
                                      20],  # font size is 20
                                     [2,  # font color code
                                      0x345678  # font color hex code
                                      ]],
                    'transform_effect': [[1, 50],
                                         [2, 0xffeeff]],
                    'timing': "",  # timing is None mean mean duration = duration sub line
                    'accel': 0.8
                }

            },
            'output': os.path.join(test_data_dir, 'preview_nhammatthaymuahe.mp4')
        }
        response = requests.post('http://localhost:8000/build_mv',
                                 json=build_template)
        print(response.headers)
        print(response.content)

    def test_build_mv_release(self):
        """

        """
        build_mv = {
            "type": 1,
            "song_info": {
                "song_file": ngaychuagiongbao_audiofile,
                "lyric_file": lyric_file,
                "title": "Ngày chưa giông bão",
                "title_file": titlefile,
                "Singer": "Bùi Lan Hương",
                "Author": "Phan Mạnh Quỳnh"
            },
            "background_info": {
                "bg_file": bg_img00,
                "sub_info": {
                    'rectangle': [100, 100, 400, 300],
                    'fontname': 'UTM Centur',
                    'fontcolor': 0x018CA7,
                    'fontsize': 40
                },
                "title_info": {
                    'rectangle': [100, 100, 0, 0],  # must has
                    'fontname': 'UTM Centur',  # Can be None
                    'fontcolor': 0x018CA7,  # Can be None
                    'fontsize': 40  # Can be None
                }
            },
            "effect_info": {
                'affect_file': affect_file,
                'opacity': 25
            }
            , 'output': os.path.join(test_data_dir, 'release_nhammatthaymuahe.mp4')
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


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


class Test_RenderCmder(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(curDir, 'request.json'), 'r', encoding='UTF-8') as json5file:
            self.data = json.load(json5file)
        pass

    def test_load_render_api(self):
        from handler import handler_render
        retval = ""
        try:
            retval = handler_render(self.data)
        except Exception as exp:
            from backend.yclogger import slacklog
            from backend.yclogger import stacklogger
            print(stacklogger.format(exp))
            # slacklog.error(stacklogger.format(exp))
        finally:
            print(retval)

    def test_handler_publish(self):
        from handler import handler_render
        from handler import handler_publish
        retval = handler_render(self.data)
        print(retval)
        body = {'id': '1iyvAl5hMN-kwTEHiTJzymZt65Vn7mCGu'}
        handler_publish()
        #
        # test = {'id': '1L0vK-3dOg7RroqrSDA-7UyR5WcEXI7bz'}
        #
        # rest_api = 'https://us-central1-ytcreator.cloudfunctions.net/publish'
        # response = requests.post(rest_api,
        #                          json=test)
        #
        # print(response.headers)
        # print(response.content)
        # # while True:
        #     import time
        #     time.sleep(1)

    def test_server_send_render_api(self):
        rest_api = 'https://us-central1-ytcreator.cloudfunctions.net/render'
        response = requests.post(rest_api,
                                 json=self.data)
        print(response.headers)
        print(response.content)

    def test_local_send_render_api(self):
        rest_api = r'http://127.0.0.1:5000/api/video/render'
        response = requests.post(rest_api,
                                 json=self.data)
        print(response.content)

    def test_crawl_nct_url(self):
        url = r'https://www.nhaccuatui.com/bai-hat/chi-can-anh-noi-mei.AjyxRsfbKTld.html'
        rest_api = 'http://localhost:8000/api/song?url='
        response = requests.get(rest_api + url)
        print(response.text)

    def test_lyric_effect(self):
        self.url = r'http://127.0.0.1:5000/lyriceffect'
        files = {'ass_in': open('test_create_mv.json5').read()}
        r = requests.post(self.url, json=files)
        print(r.text)

    def test_song_crawler(self):
        self.url = r'http://127.0.0.1:5000/songcrawler?url={}'.format(nct_url)
        r = requests.get(self.url)
        print(r.text)

    def test_publish(self):
        info = {'id': '1msM3spgPW0qIcD-wcqZ6C0lsxjVDwV_c'}
        ret = publish_vid(info)
        print("{}".format(ret))

        # rest_api = 'https://us-central1-ytcreator.cloudfunctions.net/publish'
        # response = requests.post(rest_api,
        #                          json=info)
        # print(response.headers)
        # print(response.content)


if __name__ == '__main__':
    unittest.main()
