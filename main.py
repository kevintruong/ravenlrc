#!/usr/bin/env python3
from flask import abort, Flask
from flask import jsonify

app = Flask(__name__)


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
        return jsonify(songinfo), 200, headers
    except Exception as exp:
        return error_msg_handle(exp), 404, headers
    pass


# @app.route('/api/video/render', methods=['POST'])
def render(request):
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
    if request.method != 'POST':
        return abort(405)
    try:
        import json
        from render.engine import BackgroundsRender
        from backend.yclogger import telelog
        body = request.get_json()
        telelog.debug(body)
        song_render = BackgroundsRender(body)
        retval = song_render.run()
        return '{}'.format(retval), 200, headers
    except Exception as exp:
        return error_msg_handle(exp), 404, headers

# if __name__ == '__main__':
#     app.run(debug=True)
