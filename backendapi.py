import hug
import sys

from backend.BackendCmder import *
from backend.TeleBot.GDriveFileManager import *


# sys.path.append("pycharm-debug-py3k.egg")
# import pydevd


# pydevd.settrace('172.27.39.177', port=1234, stdoutToServer=True,
#                 stderrToServer=True)


@hug.post('/crawl')
def crawl(body):
    # body is dictbuild_mv
    print(body)
    cmder: Cmder = CrawlCmder(body)
    return cmder.run()


@hug.post('/render')
def render(body):
    try:
        cmder: Cmder = RenderCmder(body)
        ret = cmder.run()
        gdrive_share_link = YtCreatorGDrive().get_share_link(ret)
        if gdrive_share_link:
            ret = gdrive_share_link
    except Exception as exp:
        return {'status': 'error',
                'message': "{}".format(exp)
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
