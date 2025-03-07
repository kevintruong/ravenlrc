import hug

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
    from backend.yclogger import slacklog
    from backend.yclogger import stacklogger
    tracebackmsg = stacklogger.format(exp)
    slacklog.error("{}".format(tracebackmsg))
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
        cmder = CrawlCmder({'url': url})
        songinfo = cmder.run()
        return songinfo.toJSON()
    except Exception as exp:
        return error_msg_handle(exp)


@hug.post('/api/video/render')
def publish(body):
    try:
        from Api.publish import publish_vid
        from handler import handler_publish
        from handler import handler_render
        from backend.yclogger import telelog
        telelog.info(body)
        status = handler_render(body)
        return status
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': 'render started'}


#
#
@hug.post('/api/video/publish')
def publish(body):
    try:
        from Api.publish import publish_vid
        from handler import handler_publish
        from backend.yclogger import telelog
        telelog.info('RELEASE: {}'.format(body))
        status = handler_publish(body)
        return status
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': 'render started'}



#
#
@hug.post('/api/video/filmrecap')
def film_recap(body):
    try:
        from Api.publish import publish_vid
        from handler import handler_filmmaker
        from backend.yclogger import telelog
        telelog.info('RELEASE: {}'.format(body))
        status = handler_filmmaker(body)
        return status
    except Exception as exp:
        return error_msg_handle(exp)
    return {'url': 'render started'}
