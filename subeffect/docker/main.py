#!/usr/bin/env python3
import json

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import werkzeug, os
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = '/tmp'


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


class LyricEffectRender(PyJSON):
    def __init__(self, d):
        super().__init__(d)


class LyricEffect(Resource):
    decorators = []

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('ass_in',
                                 type=werkzeug.datastructures.FileStorage,
                                 location='files')

    def post(self):
        json_data = request.get_json(force=True)
        if json_data:
            return {
                'data': '',
                'message': 'photo uploaded',
                'status': 'success'
            }
        return {
            'data': '',
            'message': 'Something when wrong',
            'status': 'error'
        }


api.add_resource(LyricEffect, '/lyriceffect')

if __name__ == '__main__':
    app.run(debug=True, use_debugger=False, use_reloader=False)
