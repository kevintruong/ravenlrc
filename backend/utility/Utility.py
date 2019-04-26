import os
import re

import unidecode

from backend.yclogger import telelog, slacklog


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


def check_file_existed(filepath: str):
    try:
        if not os.path.isfile(filepath):
            raise Exception("{} not found ".format(filepath))
    except Exception as exp:
        print("not found {} file".format(filepath))
        raise exp


def non_accent_convert(data: str):
    return unidecode.unidecode(data)


def create_hashtag(strtags: str):
    remove_special_char = only_latin_string(strtags)
    hashtags = '#' + remove_special_char
    return hashtags


def only_latin_string(strtags):
    remove_accent = non_accent_convert(strtags).replace(" ", "").lower()
    remove_special_char = re.sub('[^A-Za-z0-9]+', '', remove_accent)
    return remove_special_char


def generate_mv_filename(title: str):
    remove_extra_info = title.split('(', 1)[0].lower().rstrip()  # if file name content (), let get the first
    remove_accent = non_accent_convert(remove_extra_info).replace(" ", "_").lower()
    # mvfilename = only_latin_string(remove_accent)
    return remove_accent + '.mp4'


def create_mv_config_file(title: str):
    configure_file = non_accent_convert(title).replace(" ", "_").lower()
    buildfilename = configure_file + ".json5"
    return buildfilename


def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def generate_youtube_singer_hashtags(singersinfo: str):
    list_singers = singersinfo.split(',')
    append_list = []
    for each_singer in list_singers:
        nolating_singer_name = non_accent_convert(each_singer).lower()
        # onlylatin = only_latin_string(each_singer)
        append_list.append(nolating_singer_name)
        # append_list.append(onlylatin)
    return list_singers + append_list


def generate_song_hashtags(songname: str):
    songname_other = None
    songname_groups = re.search('\(([^)]+)', songname)
    if songname_groups:
        songname_other = songname_groups.group(1)
    newsongname = songname.split('(', 1)[0].lower().rstrip()
    songtags = []
    if newsongname:
        songname = newsongname

    non_accent_singname = non_accent_convert(songname.lower())
    # only_lating = only_latin_string(songname)
    songtags.append(non_accent_singname)
    songtags.append(songname.lower())
    if songname_other:
        songtags.append(songname_other)
        songtags.append(non_accent_convert(songname_other))
    return songtags


def generate_singer_song_hash_combine(singerhashtags: list, songname_hashtags: list):
    from datetime import datetime
    combine_hashtags = []
    for singer_hashtag in singerhashtags:
        length = 0
        for songname in songname_hashtags:
            combine_hashtags.append(singer_hashtag.lower() + " " + songname)
            combine_hashtags.append(songname + " lyrics")
            for each in combine_hashtags:
                length = length + len(each)
                if length > 250:
                    return combine_hashtags
                else:
                    length = 0
    return combine_hashtags


def generate_singer_song_hashtags(singers: str, songname: str):
    singer_hashtags = generate_youtube_singer_hashtags(singers)
    song_hashtags = generate_song_hashtags(songname)

    combine_hashtags = generate_singer_song_hash_combine(singer_hashtags, song_hashtags)
    final_hashtags = combine_hashtags + song_hashtags + singer_hashtags

    return final_hashtags


def clean_up(dirpath='/tmp/raven'):
    for path in os.listdir(dirpath):
        full_path = os.path.join(dirpath, path)
        if os.path.isfile(full_path):
            os.remove(full_path)
        else:
            clean_up(full_path)


def telegram_send_previewlink(url: str):
    markdown = '''[![Audi R8](http://img.youtube.com/vi/KOxbO0EI4MA/0.jpg)](https://www.youtube.com/watch?v=KOxbO0EI4MA "Audi R8")'''
    test_markdown = '''<iframe  title="YouTube video player" width="480" height="390" src="{}" frameborder="0" allowfullscreen></iframe>'''.format(
        url)
    htmlvideo = r'''<a href="{}">preview link</a>'''.format(url)
    telelog.debug(test_markdown)


import json


class PyJSON(object):
    def __init__(self, d):
        if type(d) is str:
            d = json.loads(d)
        self.from_dict(d)

    def from_dict(self, d):
        self.__dict__ = {}
        for key, value in d.items():
            if type(value) is dict:
                value = PyJSON(value)
            self.__dict__[key] = value

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if type(value) is PyJSON:
                value = value.to_dict()
            d[key] = value
        return d

    def __repr__(self):
        return str(self.to_dict())

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


import unittest


class Test_no_accent_vietnames(unittest.TestCase):
    def test_generate_youtube_singer_hashtags(self):
        test = "Hà Anh Tuấn"
        song = "Em à (Ost hello world)"
        hashtags = generate_youtube_singer_hashtags(test)
        song_hashtags = generate_song_hashtags(song)
        combine_hashtags = generate_singer_song_hash_combine(hashtags, song_hashtags)
        print(hashtags)
        print(song_hashtags)
        print(combine_hashtags)
        pass

    def test_telegram_html(self):
        slacklog.info(
            "<https://drive.google.com/a/student.sbccd.edu/uc?id=17TsP4ZkaO9wmoEuYqxwCTHbHPbCahb4d&export=download>")

    def test_generate_singer_song_hashtags(self):
        test = "Hà Anh Tuấn"
        song = "Em à (Ost hello world)"
        hashtags = generate_singer_song_hashtags(test, song)
        lenth = 0
        for each in hashtags:
            lenth = lenth + len(each)
        print(lenth)
        print(hashtags)

    def test_hello_vietnam(self):
        test = "Em À"
        print(non_accent_convert(test))
        test = 'xin chào, đây là bài hát của tôi '
        print(non_accent_convert(test))

    def test_create_file_config(self):
        print(create_mv_config_file('Tết đến xuân về'))
        clean_up('/tmp/raven/cache')

    def test_crete_hashtag(self):
        test = "Hà Anh Tuấn"
        song = "Tuyết rơi mùa hè &%^&%^$%^$^%"
        print(create_hashtag(test))
        print(create_hashtag(song))


class TestUnility(unittest.TestCase):
    def test_get_name_extention(self):
        get_filepath_info(__file__)

    def test_file_info(self):
        file = FileInfo(__file__)
        print(file.toJSON())
