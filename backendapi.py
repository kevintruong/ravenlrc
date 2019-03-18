import traceback

import hug

from backend.BackendCmder import *
from backend.Storage.GDriveFileManager import *


# sys.path.append("pycharm-debug-py3k.egg")
# import pydevd


# pydevd.settrace('172.27.39.177', port=1234, stdoutToServer=True,
#                 stderrToServer=True)


@hug.get('/api/song')
def song(url):
    try:
        # body is dictbuild_mv
        print(url)
        cmder: Cmder = CrawlCmder({'url': url})
        return cmder.run()
    except Exception as exp:
        print("exception here")
        print("*" * 60)
        tracebackmsg = traceback.format_exc()
        print(tracebackmsg)
        print("*" * 60)
        return {'status': 'error',
                'message': "{}".format(exp),
                'traceback': "{}".format(tracebackmsg)
                }


@hug.post('/api/video/render')
def render(body):
    try:
        cmder: Cmder = RenderCmder(body)
        ret = cmder.run()
    except Exception as exp:
        print("exception here")
        print("*" * 60)
        tracebackmsg = traceback.format_exc()
        print(tracebackmsg)
        print("*" * 60)
        return {'status': 'error',
                'message': "{}".format(exp),
                'traceback': "{}".format(tracebackmsg)
                }
    return {'url': ret}

#
#
# @hug.post('/build_template')
# def build_template(body):
#     return {'post_message': body}
#
#
# @hug.post('/build_album')
# def build_album(body):
#     return {'post_message': body}
