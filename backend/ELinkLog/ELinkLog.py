import json
import os
from pythonjsonlogger.jsonlogger import JsonFormatter

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

DEFAULT_LOGDIR = os.path.join(os.path.dirname(__file__), '..\\testlog')
if not os.path.isdir(DEFAULT_LOGDIR):
    os.mkdir(DEFAULT_LOGDIR)


class ELinkLogCriticalFormatter(JsonFormatter):

    def format(self, record):
        jsonrecord = super().format(record)
        self.update_record(jsonrecord)
        return jsonrecord

    def update_record(self, record):
        """
        update json record to db
        input record and update the
        (devid text ,
                  testid text,
                  asctime text,
                  filename text,
                  lineno text,
                  message text,
                  info text
        :param record: json log info
        :return:
        """
        jsonrecord = json.loads(record)
        devid = jsonrecord['devid']
        testid = jsonrecord['testid']
        loglevel = jsonrecord['levelname']

        logfile = os.path.join(DEFAULT_LOGDIR, '{}_{}_{}.json'.format(loglevel, devid, testid))

        with open(logfile, 'a') as file:
            json.dump(jsonrecord, file)
            file.write('\n')


class ELinkLogFormatter(JsonFormatter):

    def format(self, record):
        jsonrecord = super().format(record)
        self.update_record(jsonrecord)
        return jsonrecord

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_record(self, record):
        """
        update json record to db
        input record and update the
        (devid text ,
                  testid text,
                  asctime text,
                  filename text,
                  lineno text,
                  message text,
                  info text
        :param record: json log info
        :return:
        """
        jsonrecord = json.loads(record)
        values = []
        for value in jsonrecord.values():
            values.append(value)
        devid = jsonrecord['devid']
        testid = jsonrecord['testid']
        devid = devid.replace(":", "-")

        logfile = os.path.join(DEFAULT_LOGDIR, '{}_{}.json'.format(devid, testid))
        if not os.path.isfile(logfile):
            with open(logfile, 'w') as file:
                json.dump(jsonrecord, file)
        else:
            with open(logfile, 'r') as file:
                jsondata = json.load(file)
            with open(logfile, 'w') as file:
                for key in jsondata.keys():
                    if 'info' in key:
                        jsonrecord[key] = jsonrecord[key] + jsondata[key]
                json.dump(jsonrecord, file, indent=4)
