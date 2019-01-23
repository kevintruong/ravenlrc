import json
import os


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


import unittest


class TestUnility(unittest.TestCase):
    def test_get_name_extention(self):
        get_filepath_info(__file__)

    def test_file_info(self):
        file = FileInfo(__file__)
        print(file.toJSON())
