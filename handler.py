import json


def handler_render(body):
    """
    handler render endpoint
    :param body: json data (SongAPI)
    :return:
    """
    from render.engine import BackgroundsRender
    from backend.yclogger import slacklog
    # Set CORS headers for the main request
    slacklog.info(body)
    song_render = BackgroundsRender(body)
    retval = song_render.run()
    retval.fileinfo['id'] = song_render.config_id
    return retval.fileinfo
    pass


def handler_publish(body):
    """
    handler publish endpoint
    :param body:  {'id': config_id}
    :return:
    """
    from render.engine import RenderThread
    from render.engine import RenderThreadQueue

    if 'id' not in body:
        raise Exception('Not found configure id in body {}'.format(body))
    id = body['id']
    from backend.storage.gdrive import GDriveMnger
    configfile = GDriveMnger(False).download_file(id)
    with open(configfile, 'r', encoding='utf-8') as fd:
        jsondata = json.load(fd)
    rendertype = {'type': 'publish'}
    song_render = RenderThread(jsondata,
                               rendertype)
    RenderThreadQueue.get_renderqueue().add(song_render)


import unittest


class test_handlers(unittest.TestCase):
    def test_publish(self):
        info = {
            'id': '1Z4rLzJwNPmmwJ9B2LZLhtAfgEokvC8MT'
        }
        handler_publish(info)

    def test_send_publish(self):
        from Api.publish import publish_vid
        info = {
            'id': '1Z4rLzJwNPmmwJ9B2LZLhtAfgEokvC8MT'
        }
        publish_vid(info)
