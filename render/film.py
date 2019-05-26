from abc import ABC
from threading import Thread

from backend.storage.content import FilmFile, CachedContentDir, ContentFileInfo
from render.engine import RenderTiming, SongRenderEngine, RenderType, Font, SrtTempfile, AssTempfile
from render.ffmpegcli import FfmpegCli
from render.footer_header import HeaderFooter


class FilmRecap:

    def __init__(self, filminfo: dict, raw=False):
        self.file = None
        self.subtitle = None
        self.timing = []
        self.sub_lang = None
        self.audio_lang = None

        for key, value in filminfo.items():
            if key == 'file':
                self.file = value
            if key == 'subtitle':
                self.subtitle = value
            if key == 'timing':
                self.initial_timing(value, raw)
            if key == 'audio_lang':
                self.audio_lang = value
            if key == 'sub_lang':
                self.sub_lang = value

    def verify(self):
        self.subtitle = FilmFile.get_cachedfile(self.subtitle)
        self.file = FilmFile.get_cachedfile(self.file)

    def initial_timing(self, timing: list, raw):
        if raw:
            self.timing = timing
            return
        for each_timing in timing:
            timingobj = RenderTiming(each_timing)
            self.timing.append(timingobj)


class FilmRender(SongRenderEngine):
    def run(self, **kwargs):
        if self.cachedoutput is None:
            film_segments = []
            for each_timing in self.film.timing:
                each_timing: RenderTiming
                film_segment = self.render_film_with_timing(each_timing)
                film_segments.append(film_segment.get())
            print(film_segments)
            return self.join_film_segments(film_segments)
        else:
            return self.cachedoutput

    def join_film_segments(self, film_segments):
        # output = FilmFile.get_cached_filename(self.film.file, attribute=film_segments)
        output = FilmFile.create_cachedfile(self.output)
        outputfile = FilmFile.get_cachedfile(filename=self.output)
        if outputfile is None:
            output = FilmFile.create_cachedfile(self.output)
            FfmpegCli().concat_media_files(output, film_segments)
            CachedContentDir.gdrive_file_upload(output)
            outputfile = FilmFile.get_cachedfile(filename=self.output)
        return outputfile

    def __init__(self, film_data: dict):
        super().__init__()
        self.film = FilmRecap(film_data)
        self.film.verify()
        self.output = FilmFile.get_output_filename(film_data, '.mp4')
        self.iscached = False
        self.cachedoutput = None
        self.verify_output()

    def verify_output(self):
        self.cachedoutput = FilmFile.get_cachedfile(filename=self.output)
        pass
        # FilmFile.

    def get_audio_stream_by_lang(self, lang_selecet):
        audio_stream_info = FfmpegCli().get_audio_stream_list(self.film.file.get())
        streams = audio_stream_info['streams']
        if len(streams):
            for each_audio_stream in streams:
                if 'tags' in each_audio_stream:
                    tags = each_audio_stream['tags']
                    if 'language' in tags:
                        if tags['language'] == lang_selecet:
                            return each_audio_stream['index']
        return None

    def render_film_with_timing(self, timing: RenderTiming):
        audio_stream = None
        film_segment_name = FilmFile.get_cached_filename(self.film.file.filename,
                                                         attribute=timing)
        film_segment_file = FilmFile.get_cachedfile(film_segment_name)
        if film_segment_file is None:
            film_segment = FilmFile.create_cachedfile(film_segment_name)
            filmpath = self.film.file.get()
            srtpath = self.film.subtitle.get()
            if self.film.audio_lang:
                audio_stream = self.get_audio_stream_by_lang(self.film.audio_lang)
            ffmpegcli = FfmpegCli()
            ffmpegcli.adding_sub_to_video(srtpath, filmpath,
                                          film_segment,
                                          timing=timing,
                                          cleanup=False,
                                          audio=True,
                                          audio_stream=audio_stream)
            CachedContentDir.gdrive_file_upload(film_segment)
            film_segment_file = FilmFile.get_cachedfile(film_segment_name)
        return film_segment_file


class FilmRenderEngine(Thread):

    def __init__(self, rendertype=None):
        super().__init__()
        if rendertype is None:
            self.rendertype = RenderType()
        else:
            self.rendertype = rendertype


class TextInsert:
    def __init__(self, data: dict):
        self.text = None
        self.font = None
        for key, value in data.items():
            if key == 'text':
                self.text = value
            if key == 'font':
                self.font = Font(value)


class Footer(TextInsert):
    def __init__(self, data: dict):
        super().__init__(data)


class Header(TextInsert):
    def __init__(self, data: dict):
        super().__init__(data)


class FilmsRender(FilmRenderEngine):
    def run(self, **kwargs):
        from backend.yclogger import telelog
        joined_output = None
        if self.cachedoutput is None:
            films_output = []
            for each_film_render in self.films:
                each_film_render: FilmRender
                film_output = each_film_render.run()
                films_output.append(film_output.get())
            self.join_films(films_output)
        self.cachedoutput: ContentFileInfo
        telelog.info(self.cachedoutput.fileinfo)
        return self.cachedoutput.fileinfo

    def insert_header_footer(self):
        if self.header or self.footer:
            output = FilmFile.get_output_filename({'footer': self.footer.__dict__,
                                                   'header': self.header.__dict__},
                                                  '.mp4')
            output_file = FilmFile.get_cachedfile(output)
            if output_file is None:
                output_file = FilmFile.create_cachedfile(output)
                footerheader_output = AssTempfile().getfullpath()
                headerfootersub = HeaderFooter(self.header.text,
                                               self.footer.text,
                                               self.cachedoutput.get())
                headerfootersub.generate_header_footer_subtitle(footerheader_output)
                from backend.utility.TempFileMnger import MvTempFile
                scale_mv = MvTempFile().getfullpath()
                FfmpegCli().scale_square_ratio_paddingblack(self.cachedoutput.get(), 1280, 1280, scale_mv)
                FfmpegCli().adding_sub_to_video(footerheader_output,
                                                scale_mv,
                                                output_file,
                                                audio=True, cleanup=False)
                CachedContentDir.gdrive_file_upload(output_file)
                self.cachedoutput = FilmFile.get_cachedfile(output)
                from backend.yclogger import telelog
                telelog.info(self.cachedoutput.fileinfo)
                return self.cachedoutput.fileinfo

    def join_films(self, film_list):
        output = FilmFile.create_cachedfile(self.output)
        FfmpegCli().concat_media_files(output, film_list)
        CachedContentDir.gdrive_file_upload(output)
        self.verify_output()

    def __init__(self, filmsinfo: dict):
        super().__init__()
        self.films = []
        self.header = None
        self.footer = None
        for key, value in filmsinfo.items():
            if key == 'films':
                self.generate_filmrender(value)
            if key == 'header':
                self.header = Header(value)
            if key == 'footer':
                self.footer = Footer(value)
        self.output = FilmFile.get_output_filename({'films': filmsinfo['films']}, '.mp4')
        self.cachedoutput = None
        self.verify_output()

    def verify_output(self):
        self.cachedoutput = FilmFile.get_cachedfile(self.output)

    def generate_filmrender(self, value: list):
        for each_film in value:
            filmrender = FilmRender(each_film)
            self.films.append(filmrender)


import unittest


class TestFilmsRender(unittest.TestCase):
    def setUp(self) -> None:
        self.films_info = {
            "films": [
                {
                    "file": "[Erai-raws] One Punch Man (2019) - 06 [1080p][Multiple Subtitle].mkv",
                    "subtitle": "[Erai-raws] One Punch Man (2019) - 06 [1080p][Multiple Subtitle]_track3_[eng].ass",
                    "timing": [
                        {
                            "start": 600000,
                            "duration": 10000,
                        },
                        {
                            "start": 20000,
                            "duration": 50000
                        }
                    ]
                }, {
                    "file": "[Erai-raws] One Punch Man (2019) - 06 [1080p][Multiple Subtitle].mkv",
                    "subtitle": "[Erai-raws] One Punch Man (2019) - 06 [1080p][Multiple Subtitle]_track3_[eng].ass",
                    "timing": [
                        {
                            "start": 600000,
                            "duration": 10000
                        },
                        {
                            "start": 20000,
                            "duration": 50000
                        }
                    ]
                }
            ],
            "footer": {
                'text': 'this is my first mv',
                'font': {
                    "name": "SVN-Futura Light",
                    "color": "0xfffff2",
                    "size": 100
                }
            },
            "header": {
                'text': 'this is header kevinelg',
                'font': {
                    "name": "SVN-Futura Light",
                    "color": "0xfffff2",
                    "size": 100
                }
            },
            "renderType": {
                "type": "publish"
            }
        }

    def test_filmsrender(self):
        films_render = FilmsRender(self.films_info)
        films_render.start()
        films_render.join()
        films_render.insert_header_footer()
        print(films_render.cachedoutput.get())

    def test_send_filmrecap_req(self):
        import Api.publish
        ret = Api.publish.render_filmrecap(self.films_info)
        print(ret.text)
