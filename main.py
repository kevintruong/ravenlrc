import os
import shutil

from backend.storage.gdrive import GDriveMnger
from config.configure import BackendConfigure
from datetime import datetime, timedelta
from flask import abort

curdir = os.path.abspath(os.path.dirname(__file__))
config: BackendConfigure = BackendConfigure.get_config()
TmpCurDir = config.get_config().TmpDir

GDriveStorage = GDriveMnger.get_instance(False)
GdriveCacheStorage = GDriveMnger.get_instance(True)


def error_msg_handle(exp):
    import traceback
    from backend.yclogger import telelog
    tracebackmsg = traceback.format_exc()
    telelog.error("{}".format(exp) + '\n' + '```{}```'.format(tracebackmsg))
    return {'status': 'error',
            'message': "{}".format(exp),
            'traceback': "{}".format(tracebackmsg)
            }


def http(request):
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
    all_file = os.listdir(curdir)
    print("project file {}".format(all_file))

    shutil.copy2(os.path.join(curdir, 'request.json'), TmpCurDir)
    all_file = os.listdir(TmpCurDir)
    print("all files {}".format(all_file))
    try:
        print("start render")
        print("import module")
        from backend.render.engine import BackgroundsRender
        import json
        from backend.yclogger import telelog
        from backend.render.parser import SongApi
        print("load json request module")
        body = request.get_json()
        print("json data {}".format(body))
        telelog.debug('```{}```'.format(json.dumps(body, indent=1)))
        songapi = SongApi(body)
        song_render = BackgroundsRender(songapi)
        retval = song_render.run()
        return '{}'.format(retval), 200, headers
    except Exception as exp:
        print(error_msg_handle(exp))

# if __name__ == '__main__':
#     http(None)
