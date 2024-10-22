import json


def handler_getbgeffects():
    from backend.storage.content import ContentDir
    from backend.storage.content import StorageInfo
    effectfiles = []
    if len(effectfiles) == 0:
        storeinfo: StorageInfo = ContentDir().CacheGDriveMappingDictCls['Effect']
        dir_fid = storeinfo.id
        allfileitems = ContentDir.GDriveStorage.list_out(fid=dir_fid)
        for item in allfileitems:
            filename: str = item['name']
            var = filename.split('.')[0]
            effectfiles.append(var)
    return sorted(effectfiles)


def handler_render(body):
    """
    handler render endpoint
    :param body: json data (SongAPI)
    :return:
    """
    from render.engine import MvSongRender
    # Set CORS headers for the main request
    song_render = MvSongRender(body)
    retval = song_render.run()
    retval['id'] = song_render.config_id
    return retval
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
    try:
        id = body['id']
        from backend.storage.gdrive import GDriveMnger
        configfile = GDriveMnger(False).download_file(id)
        with open(configfile, 'r', encoding='utf-8') as fd:
            jsondata = json.load(fd)
        rendertype = {'type': 'publish'}
        song_render = RenderThread(jsondata,
                                   rendertype)
        RenderThreadQueue.get_renderqueue().add(song_render)
        return {'status', 'Render Req Added'}
    except Exception as exp:
        raise exp


def handler_filmmaker(body):
    """
    handler publish endpoint
    :param body:  {'id': config_id}
    :return:
    """
    from render.film import FilmsRender
    from render.engine import RenderThreadQueue
    from render.db import FilmReqInfoDb,FilmReq
    try:
        from backend.storage.gdrive import GDriveMnger
        bodyjson = json.loads(body)
        filmrender = FilmsRender(bodyjson)
        RenderThreadQueue.get_renderqueue().add(filmrender)
        FilmReqInfoDb().insert_film_req(FilmReq(filmreq=body))
        return {'status', 'Render Req Added'}
    except Exception as exp:
        raise exp


def handler_getcolorscheme(fileid):
    from backend.storage.gdrive import GDriveMnger
    from backend.colorz.colorz import colorz
    from backend.colorz.colorz import hexify
    try:
        configfile = GDriveMnger(False).download_file(fileid)
        with open(configfile, 'rb') as fd:
            color_scheme = colorz(fd)
        hexcolors = ()
        for pair in color_scheme:
            value = tuple(map(hexify, pair))
            hexcolors += value
        return {'data': list(hexcolors)}
    except Exception as exp:
        raise exp


import unittest


class test_handlers(unittest.TestCase):
    def test_publish(self):
        info = {'id': '1iyvAl5hMN-kwTEHiTJzymZt65Vn7mCGu'}
        handler_publish(info)
        while True:
            import time
            time.sleep(1)

    def test_send_publish(self):
        from Api.publish import publish_vid
        info = {'id': '1L0vK-3dOg7RroqrSDA-7UyR5WcEXI7bz'}
        ret = publish_vid(info)
        print('{}'.format(ret.text))

    def test_getcolorscheme(self):
        info = '1o578rqKCHbb0S7a9arsFAogCy1A69_pU'
        ret = handler_getcolorscheme(info)
        print(ret)

    def test_getbgeffects(self):
        effects = handler_getbgeffects()
        print(effects)
        effects = handler_getbgeffects()
        print(effects)
        effects = handler_getbgeffects()
        print(effects)
