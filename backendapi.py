import traceback

import hug

from backend.BackendCmder import *

# sys.path.append("pycharm-debug-py3k.egg")
# import pydevd


# pydevd.settrace('172.27.39.177', port=1234, stdoutToServer=True,
#                 stderrToServer=True)
from backend.yclogger import telelog


@hug.get('/api/song')
def song(url):
    try:
        # body is dictbuild_mv
        print(url)
        cmder: Cmder = CrawlCmder({'url': url})
        return cmder.run()
    except Exception as exp:
        return error_msg_handle(exp)


@hug.post('/api/video/render')
def render(body):
    try:
        cmder: Cmder = SongApi(body)
        ret = cmder.run()
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': ret}


def error_msg_handle(exp):
    tracebackmsg = traceback.format_exc()
    telelog.debug("{}".format(exp) + '\n' + tracebackmsg)
    return {'status': 'error',
            'message': "{}".format(exp),
            'traceback': "{}".format(tracebackmsg)
            }
