import logging.config

from pythonjsonlogger import jsonlogger
from structlog import configure, processors, stdlib, threadlocal


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def __init__(self, *args, **kwargs):
        self.sqliteDb = None
        super().__init__(*args, **kwargs)

    def set_sqliteDb(self, sqldb=None):
        self.sqliteDb = sqldb

    def parse(self):
        return jsonlogger.JsonFormatter.parse(self)

    def format(self, record):
        return super().format(record)


DEFAULT_CONFIGURE = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            'format': '%(lineno)d %(message)s'
            # 'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    },
    'handlers': {
        'jsonfile': {
            'class': 'logging.FileHandler',
            'formatter': 'json',
            'filename': 'ytdebug.log'
        }
    },
    'loggers': {
        'kendebug': {
            'handlers': ['jsonfile'],
            'level': logging.DEBUG
        }
    }
}

logging.config.dictConfig(DEFAULT_CONFIGURE)
configure(
    context_class=threadlocal.wrap_dict(dict),
    logger_factory=stdlib.LoggerFactory(),
    wrapper_class=stdlib.BoundLogger,
    processors=[
        stdlib.filter_by_level,
        stdlib.add_logger_name,
        stdlib.add_log_level,
        stdlib.PositionalArgumentsFormatter(),
        processors.TimeStamper(fmt="iso"),
        processors.StackInfoRenderer(),
        processors.format_exc_info,
        processors.UnicodeDecoder(),
        stdlib.render_to_log_kwargs]
)
