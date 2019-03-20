import traceback

import hug

from backend.render.engine import BackgroundsRender
from backend.render.parser import *

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


@hug.get('/api/song')
def song(url):
    try:
        telelog.debug('```{}```'.format(json.dumps(url, indent=1)))
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
