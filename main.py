#!/usr/bin/env python3
from flask import abort, Flask
from flask import request
from flask import jsonify

app = Flask(__name__)


def error_msg_handle(exp):
    import traceback
    from backend.yclogger import telelog
    tracebackmsg = traceback.format_exc()
    telelog.error("{}".format(exp) + '\n' + '```{}```'.format(tracebackmsg))
    return {'status': 'error',
            'message': "{}".format(exp),
            'traceback': "{}".format(tracebackmsg)
            }


@app.route('/api/songcrawler')
def songcrawler():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method != 'GET':
        return abort(405)
    try:
        from backend.yclogger import telelog
        from render.parser import CrawlCmder
        from render.parser import Cmder
        url = request.args.get('url')
        telelog.debug('```{}```'.format(url))
        cmder: Cmder = CrawlCmder({'url': url})
        songinfo = cmder.run()
        return jsonify(songinfo), 200, headers
    except Exception as exp:
        return error_msg_handle(exp)

    pass


@app.route('/api/video/render', methods=['POST'])
def render():
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
        from render.engine import BackgroundsRender
        import json
        from backend.yclogger import telelog
        from render.parser import SongApi
        body = request.get_json()
        songapi = SongApi(body)
        song_render = BackgroundsRender(songapi)
        retval = song_render.run()
        return '{}'.format(retval), 200, headers
    except Exception as exp:
        print(error_msg_handle(exp))


if __name__ == '__main__':
    app.run(debug=True)
