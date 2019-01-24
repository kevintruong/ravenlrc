import json
import os
import unidecode


def get_filepath_info(filepath: str):
    filename = os.path.basename(filepath)
    dirname = os.path.dirname(filepath)
    name, ext = filename.split('.')

    print(filepath)
    print(dirname)
    print(filename)
    print(name)
    print(ext)
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
    remove_accent = non_accent_convert(strtags).replace(" ", "").lower()
    hashtags = '#' + remove_accent
    return hashtags


def create_mv_config_file(title: str):
    configure_file = non_accent_convert(title).replace(" ", "_").lower()
    buildfilename = configure_file + ".json5"
    return buildfilename


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
        song = "Tuyết rơi mùa hè"
        print(create_hashtag(test))
        print(create_hashtag(song))


class TestUnility(unittest.TestCase):
    def test_get_name_extention(self):
        get_filepath_info(__file__)

    def test_file_info(self):
        file = FileInfo(__file__)
        print(file.toJSON())
