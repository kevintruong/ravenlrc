import ast
import json

import requests

# RENDER_ENDPOINT = 'https://ravpublish.herokuapp.com/'
#
RENDER_ENDPOINT = 'http://172.17.0.2:5000'
# RENDER_ENDPOINT = 'http://35.236.11.179:5000'



def toJSON(objinfo):
    data = json.dumps(objinfo, default=lambda o: o.__dict__)
    return ast.literal_eval(data)


def publish_vid(body):
    r = requests.post(RENDER_ENDPOINT + '/api/video/publish', json=body)
    return r
