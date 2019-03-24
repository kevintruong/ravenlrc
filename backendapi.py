import traceback

import hug

from backend.render.engine import BackgroundsRender
from backend.render.parser import *
from hug_middleware_cors import CORSMiddleware

# api = hug.API(__name__)
# api.http.add_middleware(CORSMiddleware(api))

# sys.path.append("pycharm-debug-py3k.egg")
# import pydevd


# pydevd.settrace('172.27.39.177', port=1234, stdoutToServer=True,
#                 stderrToServer=True)
from backend.storage.gdrive import GDriveMnger
from backend.yclogger import telelog


def error_msg_handle(exp):
    tracebackmsg = traceback.format_exc()
    telelog.error("{}".format(exp) + '\n' + '```{}```'.format(tracebackmsg))
    return {'status': 'error',
            'message': "{}".format(exp),
            'traceback': "{}".format(tracebackmsg)
            }


# @hug.response_middleware()
# def CORS(request, response, resource):
#     response.set_header('Access-Control-Allow-Origin', '*')
#     response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#     response.set_header(
#         'Access-Control-Allow-Headers',
#         'Authorization,Keep-Alive,User-Agent,'
#         'If-Modified-Since,Cache-Control,Content-Type'
#     )
#     response.set_header(
#         'Access-Control-Expose-Headers',
#         'Authorization,Keep-Alive,User-Agent,'
#         'If-Modified-Since,Cache-Control,Content-Type'
#     )


def cors_support(response, *args, **kwargs):
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
    response.set_header('Access-Control-Allow-Headers', 'X-Requested-With,content-type')
    response.setHeader('Access-Control-Allow-Credentials', True)


api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))


@hug.get('/api/song')
def song(url):
    print(url)
    try:
        telelog.debug('```{}```'.format(url))
        cmder: Cmder = CrawlCmder({'url': url})
        return cmder.run()
    except Exception as exp:
        return error_msg_handle(exp)


@hug.post('/api/video/render')
def render(body):
    try:
        telelog.debug('```{}```'.format(json.dumps(body, indent=1)))
        songapi = SongApi(body)
        song_render = BackgroundsRender(songapi)
        ret = song_render.run()
        sharelink = GDriveMnger().get_share_link(ret)
        if sharelink:
            ret = sharelink
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': ret}
