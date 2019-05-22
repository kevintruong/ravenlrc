import json
import requests

from config.configure import BackendConfigure

# SONGCRAWLER__ENDPOINT = 'http://35.197.57.162:5000/'

configure: BackendConfigure = BackendConfigure.get_config()
SONGCRAWLER__ENDPOINT = configure.EndPoint


# SONGCRAWLER__ENDPOINT = 'http://localhost:5000/'

def get_song_info(url):
    rsp = requests.get(SONGCRAWLER__ENDPOINT + 'api/song?url={}'.format(url))
    songinfo: str = json.loads(rsp.content.decode('utf-8'))
    return songinfo
