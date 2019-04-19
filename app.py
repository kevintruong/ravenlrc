import hug
import traceback

api = hug.API(__name__)
api.http.add_middleware(hug.middleware.CORSMiddleware(api, max_age=10))


@hug.response_middleware()
def CORS(request, response, resource):
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.set_header('Access-Control-Allow-Headers',
                        'Authorization,Keep-Alive,User-Agent,'
                        'If-Modified-Since,Cache-Control,Content-Type')
    response.set_header('Access-Control-Expose-Headers',
                        'Authorization,Keep-Alive,User-Agent,'
                        'If-Modified-Since,Cache-Control,Content-Type'
                        )
    if request.method == 'OPTIONS':
        response.set_header('Access-Control-Max-Age', 1728000)
        response.set_header('Content-Type', 'text/plain charset=UTF-8')
        response.set_header('Content-Length', 0)
        response.status_code = hug.HTTP_204


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
        from crawler.cmder import CrawlCmder
        from backend.type import Cmder
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
        from render.engine import BackgroundsRender
        import json
        from backend.yclogger import telelog
        from render.parser import SongApi
        telelog.debug('```{}```'.format(json.dumps(body, indent=1)))
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': 'render started'}
