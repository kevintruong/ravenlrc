from abc import ABC

from backend.storage.content import FilmFile, CachedContentDir
from render.engine import RenderTiming, SongRenderEngine
from render.ffmpegcli import FfmpegCli


class FilmRecap:

    def __init__(self, filminfo: dict):
        self.file = None
        self.subtitle = None
        self.timing = []

        for key, value in filminfo.items():
            if key == 'file':
                self.file = value
                self.file = FilmFile.get_cachedfile(self.file)
            if key == 'subtitle':
                self.subtitle = value
                self.subtitle = FilmFile.get_cachedfile(self.subtitle)
            if key == 'timing':
                self.initial_timing(value)

    def initial_timing(self, timing: list):
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
        self.output = FilmFile.get_output_filename(film_data, '.mp4')
        self.iscached = False
        self.cachedoutput = None
        self.verify_output()

    def verify_output(self):
        self.cachedoutput = FilmFile.get_cachedfile(filename=self.output)
        pass
        # FilmFile.

    def render_film_with_timing(self, timing: RenderTiming):
        film_segment_name = FilmFile.get_cached_filename(self.film.file.filename,
                                                         attribute=timing)
        film_segment_file = FilmFile.get_cachedfile(film_segment_name)
        if film_segment_file is None:
            film_segment = FilmFile.create_cachedfile(film_segment_name)
            filmpath = self.film.file.get()
            srtpath = self.film.subtitle.get()
            ffmpegcli = FfmpegCli()
            ffmpegcli.adding_sub_to_video(srtpath, filmpath, film_segment, timing=timing, cleanup=False, audio=True)
            CachedContentDir.gdrive_file_upload(film_segment)
            film_segment_file = FilmFile.get_cachedfile(film_segment_name)
        return film_segment_file


class FilmsRender(SongRenderEngine):
    def run(self, **kwargs):
        if self.cachedoutput is None:
            films_output = []
            for each_film_render in self.films:
                each_film_render: FilmRender
                film_output = each_film_render.run()
                films_output.append(film_output.get())
            self.join_films(films_output)

    def join_films(self, film_list):
        output = FilmFile.create_cachedfile(self.output)
        FfmpegCli().concat_media_files(output, film_list)
        CachedContentDir.gdrive_file_upload(output)
        FilmFile.get_cachedfile(filename=self.output)
        print(output)

    def __init__(self, filmsinfo: dict):
        super().__init__()
        self.films = []
        for key, value in filmsinfo.items():
            if key == 'films':
                self.generate_filmrender(value)
        self.output = FilmFile.get_output_filename(filmsinfo, '.mp4')
        self.cachedoutput = None

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
                            "start": 10000,
                            "duration": 40000
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
                            "start": 10000,
                            "duration": 40000
                        }
                    ]
                }
            ],
            "renderType": {
                "type": "publish"
            }
        }

    def test_filmsrender(self):
        films_render = FilmsRender(self.films_info)
        films_render.run()
