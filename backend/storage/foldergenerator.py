import os

import pandas as pd


class SchemmaGenerator:
    def __init__(self, jsonfile: str, cwdpath: str):
        self.file = jsonfile
        self.path = cwdpath
        if not os.path.exists(cwdpath):
            raise NotADirectoryError

    def get_json(self, path):
        """Returns the json data as data frame"""
        with open(path) as fd:
            return [x for x in pd.read_json(path)['root']]

    def create_folder(self, path):
        path = self.path + '/' + path
        '''Attempts to create a folder at specified path
        Returns success. TODO: store fails, and allow for
        re-attempt
        '''
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                return True
        except OSError:
            print('Error: Creating directory. ' + path)
            return False

    def parse(self, json):
        """Returns the folders we want from json"""
        structure = self.get_json(json)
        return [x for folder in structure for x in folder]

    def generate_parents(self, items):
        """Creates top level folders"""
        [self.create_folder(items[i]['name'])
         for i, folder in enumerate(items) if items[i]['type'] == 'folder']

    def generate_children(self, items):
        """ Creates children folders, if any exist """
        [self.create_folder(str(i['name']) + '/' + str(c['name']))
         for i in items if 'children' in i for c in i['children'
         ]]

    def generate_children_of_children(self, items):
        """ Creates children folders, if any exist """
        for i in items:
            if 'children' in i:
                for c in i['children']:
                    if 'children' in c:
                        for cc in c['children']:
                            self.create_folder(str(i['name']) + '/' + str(c['name']) + '/' + str(cc['name']))

    def generate(self):
        """Takes in path to json and creates folders"""
        items = self.parse(self.file)
        self.generate_parents(items)
        self.generate_children(items)
        self.generate_children_of_children(items)


import unittest


class Test_FoldersGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = SchemmaGenerator('Storage.json', '/tmp')

    def test_generator_folder(self):
        self.generator.generate()

    pass
