import json
import os
import re

import unidecode


def get_filepath_info(filepath: str):
    filename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)
    name, ext = filename.split('.')
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
    remove_accent = non_accent_convert(title).replace(" ", "_").lower()
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


import unittest


class Test_no_accent_vietnames(unittest.TestCase):
    def test_hello_vietnam(self):
        test = "Em À"
        print(non_accent_convert(test))
        test = 'xin chào, đây là bài hát của tôi '
        print(non_accent_convert(test))

    def test_create_file_config(self):
        print(create_mv_config_file('Tết đến xuân về'))

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
