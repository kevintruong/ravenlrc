#!/usr/bin/env python3
import flask
from flask import abort, Request
from flask import jsonify


# app = Flask(__name__)


def error_msg_handle(exp):
    import traceback
    from backend.yclogger import telelog
    tracebackmsg = traceback.format_exc()
    telelog.error("{}".format(exp) + '\n' + '```{}```'.format(tracebackmsg))
    return str({'status': 'error',
                'message': "{}".format(exp),
                'traceback': "{}".format(tracebackmsg)
                })


# @app.route('/api/songcrawler')
def songcrawler(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'GET':
        return abort(405)
    try:
        from backend.yclogger import telelog
        from crawler.cmder import CrawlCmder
        from backend.type import Cmder
        url = request.args.get('url')
        telelog.debug('```{}```'.format(url))
        cmder: Cmder = CrawlCmder({'url': url})
        songinfo = cmder.run()
        response = flask.jsonify(songinfo)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST')
        return response
    except Exception as exp:
        return error_msg_handle(exp), 404, headers
    pass


def colorscheme(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'GET':
        return abort(405)
    try:
        from handler import handler_getcolorscheme
        fileid = request.args.get('id')
        color_scheme = handler_getcolorscheme(fileid)
        response = flask.jsonify(color_scheme)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST')
        return response
    except Exception as exp:
        return error_msg_handle(exp), 404, headers
    pass


# @app.route('/api/songcrawler')
def bgeffect(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'GET':
        return abort(405)
    try:
        from handler import handler_getbgeffects
        ret = handler_getbgeffects()
        response = flask.jsonify({'data': ret})
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST')
        return response
    except Exception as exp:
        return error_msg_handle(exp), 404, headers
    pass


# @app.route('/api/video/render', methods=['POST'])
def render(request: Request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'POST' and request.method != 'OPTIONS':
        return abort(405)
    try:
        import json
        from render.engine import BackgroundsRender
        from backend.yclogger import slacklog
        from backend.yclogger import telelog
        from handler import handler_render

        # Set CORS headers for the preflight request
        if request.method == 'OPTIONS':
            # Allows GET requests from any origin with the Content-Type
            # header and caches preflight response for an 3600s
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return '', 204, headers

        # Set CORS headers for the main request
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        body = request.get_json()
        slacklog.debug(body)
        retval = handler_render(body)
        response = flask.jsonify(retval)
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        return response
    except Exception as exp:
        return error_msg_handle(exp), 404, headers


def publish(request: Request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'POST' and request.method != 'OPTIONS':
        return abort(405)
    try:

        # Set CORS headers for the preflight request
        if request.method == 'OPTIONS':
            # Allows GET requests from any origin with the Content-Type
            # header and caches preflight response for an 3600s
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return '', 204, headers

        from Api.publish import publish_vid
        from backend.yclogger import slacklog
        # Set CORS headers for the main request
        body = request.get_json()
        slacklog.info(body)
        return publish_vid(body)
    except Exception as exp:
        return error_msg_handle(exp), 404, headers

# if __name__ == '__main__':
#     app.run(debug=True)
