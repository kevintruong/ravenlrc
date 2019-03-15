import hug
import sys

from backend.BackendCmder import *


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
    cmder: Cmder = RenderCmder(body)
    ret = cmder.run()
    return {'output': ret}
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
