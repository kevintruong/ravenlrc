import json
import requests

SONGCRAWLER__ENDPOINT = 'http:///localhost:5000'


def get_song_info(url):
    rsp = requests.get(SONGCRAWLER__ENDPOINT + 'api/song?url={}'.format(url))
    songinfo: str = json.loads(rsp.content.decode('utf-8'))
    return songinfo
