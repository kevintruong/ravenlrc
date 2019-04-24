import ast
import json
import requests
from render.type import BgLyric, Size

SONGEFFECT_ENDPOINT = 'https://subeffect.herokuapp.com'


# SONGEFFECT_ENDPOINT = 'http://172.17.0.2:5000'


def toJSON(objinfo):
    data = json.dumps(objinfo, default=lambda o: o.__dict__)
    return ast.literal_eval(data)


def generate_songeffect_for_lrc(effectname, lrccontent, config: BgLyric, resolution=None):
    resolution: Size
    jsondata = {
        'effectname': effectname,
        'lrccontent': lrccontent,
        'config': toJSON(config),
        'resolution': toJSON(resolution)
    }
    strjson = json.dumps(jsondata)
    jsondata = json.loads(strjson)
    headers = {"Accept-Encoding": "gzip"}
    r = requests.post(SONGEFFECT_ENDPOINT + '/api/lrceffect', json=jsondata, headers=headers)
    songeffect: str = json.loads(r.content.decode('utf-8'))['data']
    return songeffect


def get_song_effect_list():
    pass


import unittest
import os


class Test_SongEffect(unittest.TestCase):
    CurDir = os.path.dirname(os.path.realpath(__file__))

    def setUp(self) -> None:
        import json
        self.lrcfile = os.path.join(self.CurDir, '../subeffect/test/nested.lrc')
        with open(self.lrcfile, 'r') as assfile:
            self.lrccontent = assfile.read()

        from type import BgLyric
        self.config = BgLyric({
            "position": {
                "x": "221",
                "y": "500"
            },
            "size": {
                "width": "891",
                "height": "243"
            },
            "font": {
                "name": "UTM Silk Script",
                "color": "0xFFFFFF",
                "size": "80"
            }
        })
        self.resolution = Size({
            'width': "1280",
            'height': "720"
        })
        self.effectname = 'Trans_Eff_019'

    def test_gen_songeffect(self):
        ret = generate_songeffect_for_lrc(self.effectname, self.lrccontent, self.config, resolution=self.resolution)
        print(ret)
