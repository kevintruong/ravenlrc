import json

import requests

from render.type import BgLyric

SONGEFFECT_ENDPOINT = 'https://subeffect.herokuapp.com'


def generate_songeffect_for_lrc(effectname, lrccontent, config:BgLyric):
    jsondata = {
        'effectname': effectname,
        'lrccontent': lrccontent,
        'config': config.toJSON()
    }
    strjson = json.dumps(jsondata)
    jsondata = json.loads(strjson)
    headers = {"Accept-Encoding": "gzip"}
    r = requests.post(SONGEFFECT_ENDPOINT + '/api/lrceffect', json=jsondata, headers=headers)
    songeffect: str = json.loads(r.content.decode('utf-8'))['data']
    return songeffect


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
        self.effectname = 'Trans_Eff_001'

    def test_gen_songeffect(self):
        ret = generate_songeffect_for_lrc(self.effectname, self.lrccontent, self.config)
        print(ret)
