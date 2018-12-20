import hug
import sys

from backend.BackendCmder import *

sys.path.append("pycharm-debug-py3k.egg")
import pydevd


# pydevd.settrace('172.27.39.177', port=1234, stdoutToServer=True,
#                 stderrToServer=True)


@hug.post('/crawl')
def crawl(body):
    # body is dictbuild_mv
    cmder: Cmder = CrawlCmder.get_crawlcmder(body)
    return cmder.run()


@hug.post('/build_mv')
def build_mv(body):
    cmder: Cmder = BuildCmder(body)
    cmder.run()
    return {'post_message': body}


@hug.post('/build_template')
def build_template(body):
    return {'post_message': body}


@hug.post('/build_album')
def build_album(body):
    return {'post_message': body}
