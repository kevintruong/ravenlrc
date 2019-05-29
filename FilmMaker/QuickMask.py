import fnmatch
import json
import os
from threading import Thread

from backend.storage.content import FilmFile, CachedContentDir
from render.ffmpegcli import FfmpegCli
from render.film import FilmRecap


def get_filepath_info(filepath: str):
    try:
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)
    except Exception as exp:
        dirname = None
    ext = ".{}".format(filename.split(os.extsep)[-1])
    name = "".join(filename.split(os.extsep)[:-1])
    return [dirname, filename, name, ext]


class FileInfo:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, filepath: str):
        fileinfo = get_filepath_info(filepath)
        self.dir = fileinfo[0]
        self.filename = fileinfo[1]
        self.name = fileinfo[2]
        self.ext = fileinfo[3]


class CutMask:
    def __init__(self, maskin, maskout):
        self.maskin = maskin
        self.maskout = maskout

    def create_RenderTiming(self):
        duration = self.maskout - self.maskin
        return {
            'start': self.maskin,
            'duration': duration
        }


class VideoMask:
    def __init__(self):
        self.file = None
        self.timing = []
        self.subtitle = None
        self.sub_lang = 'vie'
        self.audio_lang = 'eng'
        self.curmaskin = 0
        self.curmaskout = 0

    @staticmethod
    def toJSON(obj):
        return json.dumps(obj, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_audio_lang(self, audio_lang='eng'):
        self.audio_lang = audio_lang

    def set_subtitle_lang(self, subtitle_lang):
        self.sub_lang = subtitle_lang

    def set_subtitle_from_movie_by_lang(self, subtitle_lang='eng'):
        self.sub_lang = subtitle_lang
        self.get_subtitle_from_movie(self.sub_lang)

    def generate_filmrecap_obj(self):
        filmrecap_obj = {}
        if self.file:
            filmrecap_obj['file'] = self.file
        if self.subtitle:
            filmrecap_obj['subtitle'] = self.subtitle
        if self.timing:
            filmrecap_obj['timing'] = self.timing
        if self.audio_lang:
            filmrecap_obj['audio_lang'] = self.audio_lang
        if self.sub_lang:
            filmrecap_obj['sub_lang'] = self.sub_lang
        return filmrecap_obj

    @staticmethod
    def recursive_glob(treeroot, pattern):
        results = []
        for base, dirs, files in os.walk(treeroot):
            goodfiles = fnmatch.filter(files, pattern)
            results.extend(os.path.join(base, f) for f in goodfiles)
        return results

    def get_substream_index_by_lang(self, lang_select: str):
        ret = FfmpegCli().get_subtitle_list(self.file)
        substreams = ret['streams']
        if len(substreams):
            for each_sub_stream in substreams:
                print(json.dumps(each_sub_stream, indent=4))
                tags = each_sub_stream['tags']
                if 'language' in tags:
                    language = each_sub_stream['tags']['language']
                    if language == lang_select:
                        return each_sub_stream['index']
        print('Not found the lang_select {} in video'.format(lang_select))
        return None

    def get_video_resolution(self):
        res = FfmpegCli().get_video_resolution(self.file)
        return "{}x{}".format(res['width'], res['height'])

    def get_substreams(self):
        ret = FfmpegCli().get_subtitle_list(self.file)
        substreams_lang = []
        substreams = ret['streams']
        if len(substreams):
            for each_sub_stream in substreams:
                print(json.dumps(each_sub_stream, indent=4))
                index = each_sub_stream['index']
                tags = each_sub_stream['tags']
                if 'language' in tags:
                    language = each_sub_stream['tags']['language']
                    # substreams_lang.append([index, language])
                    subtitle_file = self.get_subtitle_from_movie(language)
                    substreams_lang.append([language, subtitle_file])
        return substreams_lang

    def extract_subtitle_from_movie_by_stream_index(self, index, langselect):
        fileinfo = FileInfo(self.file)
        subtitlefile = os.path.join(fileinfo.dir, "{}__{}.ass".format(fileinfo.name, langselect))
        if not os.path.exists(subtitlefile):
            FfmpegCli().get_subtitlefile_by_stream_inde(self.file, index, subtitlefile)
        return subtitlefile
        pass

    def get_subtitle_from_movie(self, lang_select):
        index = self.get_substream_index_by_lang(lang_select)
        sub_file = self.extract_subtitle_from_movie_by_stream_index(index, lang_select)
        if sub_file:
            from pysubs2 import SSAFile
            subs = SSAFile.load(sub_file, encoding='utf-8')  # create ass file
            for key, value in subs.styles.items():
                default_style = subs.styles[key]
                default_style.fontsize = 24
                default_style.fontname = 'Source Sans Pro'
            subs.save(sub_file)
            return sub_file
        return None

    @classmethod
    def format_subtitle(cls, sub_file, ass_subfile):
        if not os.path.exists(sub_file):
            raise FileExistsError('not found {}'.format(sub_file))
        from pysubs2 import SSAFile
        subs = SSAFile.load(sub_file, encoding='utf-8')  # create ass file
        for key, value in subs.styles.items():
            default_style = subs.styles[key]
            default_style.fontsize = 24
            default_style.fontname = 'Source Sans Pro'
            default_style.shadow = 0
            default_style.outline = 0
        subs.save(ass_subfile)
        return ass_subfile

    def set_subtitle_uri(self, subtitle_uri=None):
        if subtitle_uri:
            self.subtitle = subtitle_uri
            return
        film_fileinfo = FileInfo(self.file)
        subtitle_ass = self.recursive_glob(film_fileinfo.dir, '*.ass')
        if len(subtitle_ass):
            for each_sub in subtitle_ass:
                if film_fileinfo.name in each_sub:
                    self.subtitle = each_sub
                    return
        subtitle_srt = self.recursive_glob(film_fileinfo.dir, '*.srt')
        if len(subtitle_srt):
            for each_sub in subtitle_ass:
                if film_fileinfo.name in each_sub:
                    self.subtitle = each_sub
                    return
        print('not found any subtitle in {}'.format(film_fileinfo.dir))

    def get_audio_stream_by_lang(self, lang_selecet):
        audio_stream_info = FfmpegCli().get_audio_stream_list(self.file)
        streams = audio_stream_info['streams']
        if len(streams):
            for each_audio_stream in streams:
                if 'tags' in each_audio_stream:
                    tags = each_audio_stream['tags']
                    if 'language' in tags:
                        if tags['language'] == lang_selecet:
                            return each_audio_stream['index']
        return None

    def get_audiostreams(self):
        audio_stream_info = FfmpegCli().get_audio_stream_list(self.file)
        streams = audio_stream_info['streams']
        audiostreams_lang = []
        if len(streams):
            for each_audio_stream in streams:
                if 'tags' in each_audio_stream:
                    tags = each_audio_stream['tags']
                    if 'language' in tags:
                        language = tags['language']
                        audiostreams_lang.append(['{}'.format(each_audio_stream['index']), language])
            return audiostreams_lang
        return None

    def add_mask(self):
        if self.curmaskout == 0:
            print('mask out is 0 => need to set mask out')
            return
        mask = CutMask(self.curmaskin, self.curmaskout).create_RenderTiming()
        self.timing.append(mask)
        self.curmaskin = 0
        self.curmaskout = 0
        print('added mask {}'.format(mask))

    def set_video(self, fileurl):
        if os.path.exists(fileurl):
            self.file = fileurl
            self.set_subtitle_uri()
        print(self.file)

    def mask_in(self, timestamp: int):
        self.curmaskin = timestamp
        print('cur mask in {}'.format(self.curmaskin))

    def mask_out(self, timestamp: int):
        self.curmaskout = timestamp
        print('cur mask out {}'.format(self.curmaskout))


class FilmRenderReqMaker(Thread):
    def __init__(self, request: dict):
        super().__init__()
        self.request = request
        self.films = None

    def upload_file(self):
        films_list = self.request['films']
        file = None
        subtitle = None
        timing = None
        films_info = []
        for filminfo in films_list:
            filmrecap_obj = FilmRecap(filminfo, raw=True)
            filmrecap_obj.file = \
                CachedContentDir.gdrive_file_upload_to_dir(FilmFile.FilmDir, filmrecap_obj.file)[
                    'name']
            if filmrecap_obj.subtitle:
                filmrecap_obj.subtitle = \
                    CachedContentDir.gdrive_file_upload_to_dir(FilmFile.FilmDir, filmrecap_obj.subtitle)['name']
            films_info.append(filmrecap_obj)
        self.request['films'] = films_info
        self.films = self.request

    def run(self) -> None:
        self.upload_file()
        print(self.films)
        from Api.publish import render_filmrecap
        ret = render_filmrecap(VideoMask.toJSON(self.films))
        return ret


import unittest


class TestVideoMask(unittest.TestCase):
    def setUp(self) -> None:
        self.videomask = VideoMask()
        self.videouri = '/media/kevin/New Volume/radarr/download/First.Man.2018.2018.mHD.BluRay.DD5.1.x264-TRiM/First.Man.2018.2018.mHD.BluRay.DD5.1.x264-TRiM.mkv'

    def test_get_subtitle(self):
        self.videomask.set_video(self.videouri)
        self.videomask.get_subtitle_from_movie('vie')
        ret = self.videomask.get_audio_stream_by_lang('eng')
        print(json.dumps(ret, indent=4))
        from render.engine import RenderTiming
        FfmpegCli().adding_sub_to_video(self.videomask.subtitle,
                                        self.videomask.file,
                                        'test.mp4', audio=True,
                                        cleanup=False,
                                        timing=RenderTiming({'start': 5000000, 'duration': 100000}),
                                        audio_stream=ret
                                        )

    def test_get_video_resolution(self):
        ret = FfmpegCli().get_video_resolution(self.videouri)
        print(VideoMask.toJSON(ret))

    def test_set_subtitile(self):
        self.videomask.set_video(self.videouri)
        self.videomask.get_subtitle_from_movie('vie')
        self.videomask.audio_lang = 'eng'
        self.videomask.mask_in(50000)
        self.videomask.mask_out(100000)
        self.videomask.add_mask()
        self.videomask.mask_in(150000)
        self.videomask.mask_out(160000)
        self.videomask.add_mask()
        filminfo = self.videomask.generate_filmrecap_obj()
        films_info = {
            'films': [filminfo]
        }
        filmmaker = FilmRenderReqMaker(films_info)
        ret = filmmaker.run()
        print(ret.text)

    def test_send_render_req(self):
        req = {
            "films": [
                {
                    "file": "Incredibles.2.2018.mHD.BluRay.DD5.1.x264-TRiM.mkv",
                    "subtitle": "Incredibles22018mHDBluRayDD51x264-TRiM_vie.ass",
                    "timing": [
                        {
                            "duration": 210627,
                            "start": 1480504
                        },
                        {
                            "duration": 212197,
                            "start": 1898065
                        }
                    ]
                },
                {
                    "audio_lang": "eng",
                    "file": "Venom.2018.mHD.BluRay.DD5.1.x264-TRiM.mkv",
                    "subtitle": "Venom2018mHDBluRayDD51x264-TRiM_vie.ass",
                    "timing": [
                        {
                            "duration": 107773,
                            "start": 194582
                        },
                        {
                            "duration": 102839,
                            "start": 408209
                        }
                    ]
                }
            ],
            "footer": {
                'text': 'this is footer',
                'font': {
                    "name": "SVN-Futura Light",
                    "color": "0xfffff2",
                    "size": 100
                }
            },
            "header": {
                'text': 'this is header',
                'font': {
                    "name": "SVN-Futura Light",
                    "color": "0xfffff2",
                    "size": 80
                }
            }

        }

        from Api.publish import render_filmrecap
        ret = render_filmrecap(VideoMask.toJSON(req))
        return ret
