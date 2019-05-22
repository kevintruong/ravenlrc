import ast
import json
import requests

# RENDER_ENDPOINT = 'https://ravpublish.herokuapp.com/'
#
# RENDER_ENDPOINT = 'http://localhost:5000'
# RENDER_ENDPOINT = 'http://35.197.57.162:5000'

from config.configure import BackendConfigure


configure: BackendConfigure = BackendConfigure.get_config()
RENDER_ENDPOINT = configure.EndPoint


def toJSON(objinfo):
    data = json.dumps(objinfo, default=lambda o: o.__dict__)
    return ast.literal_eval(data)


def publish_vid(body):
    r = requests.post(RENDER_ENDPOINT + '/api/video/publish', json=body)
    return r.text, r.status_code
