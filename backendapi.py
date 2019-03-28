import hug
import traceback

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))


def error_msg_handle(exp):
    from backend.yclogger import telelog
    tracebackmsg = traceback.format_exc()
    telelog.error("{}".format(exp) + '\n' + '```{}```'.format(tracebackmsg))
    return {'status': 'error',
            'message': "{}".format(exp),
            'traceback': "{}".format(tracebackmsg)
            }


@hug.get('/api/song')
def song(url):
    try:
        from backend.yclogger import telelog
        from backend.render.parser import CrawlCmder
        from backend.render.parser import Cmder
        telelog.debug('```{}```'.format(url))
        cmder: Cmder = CrawlCmder({'url': url})
        return cmder.run()
    except Exception as exp:
        return error_msg_handle(exp)


#
#
@hug.post('/api/video/render')
def render(body):
    try:
        from backend.render.engine import BackgroundsRender
        import json
        from backend.yclogger import telelog
        from backend.render.parser import SongApi
        telelog.debug('```{}```'.format(json.dumps(body, indent=1)))
        songapi = SongApi(body)
        song_render = BackgroundsRender(songapi)
        ret = song_render.run()
        from backend.storage.gdrive import GDriveMnger
        sharelink = GDriveMnger().get_share_link(ret)
        if sharelink:
            ret = sharelink
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': ret}


@hug.post('api/video/publish')
def publish(body):
    return {'msg': 'not support yet'}
    pass


@hug.post('/api/layer/render')
def render_layer(body):
    try:
        from backend.render.engine import BackgroundsRender
        import json
        from backend.yclogger import telelog
        from backend.render.parser import SongApi
        telelog.debug('```{}```'.format(json.dumps(body, indent=1)))
        songapi = SongApi(body)
        song_render = BackgroundsRender(songapi)
        ret = song_render.run()
        from backend.storage.gdrive import GDriveMnger
        sharelink = GDriveMnger().get_share_link(ret)
        if sharelink:
            ret = sharelink
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': ret}
