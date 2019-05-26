import ast
import json
import requests

# RENDER_ENDPOINT = 'https://ravpublish.herokuapp.com/'
#
# RENDER_ENDPOINT = 'http://localhost:5000'

from config.configure import BackendConfigure

configure: BackendConfigure = BackendConfigure.get_config()
RENDER_ENDPOINT = configure.EndPoint


def toJSON(objinfo):
    data = json.dumps(objinfo, default=lambda o: o.__dict__)
    return ast.literal_eval(data)


def publish_vid(body):
    r = requests.post(RENDER_ENDPOINT + '/api/video/publish', json=body)
    return r


def render_preview_song(body):
    r = requests.post(RENDER_ENDPOINT + '/api/video/render', json=body)
    return r


def render_filmrecap(body):
    r = requests.post(RENDER_ENDPOINT + '/api/video/filmrecap', json=body)
    return r
