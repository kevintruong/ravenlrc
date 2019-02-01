import logging.config
from pythonjsonlogger import jsonlogger
from structlog import configure, processors, stdlib, threadlocal
import os

CurDir = os.path.dirname(__file__)
DebugLogDir = os.path.join(CurDir, "..//..//log")
if not os.path.isdir(DebugLogDir):
    os.mkdir(DebugLogDir)
ytDebugFile = os.path.join(DebugLogDir, "ytdebugfile.log")
debugfile = str(ytDebugFile)


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
    'formatters': {
        'telegram': {
            'class': 'telegram_handler.HtmlFormatter',
            'fmt': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'telegram': {
            'class': 'telegram_handler.TelegramHandler',
            'formatter': 'telegram',
            'token': '714001436:AAHJ54DYwZeTHAPhjFagVPKeG61nURx7GI8',
            'chat_id': '338086459'
        }
    },
    'loggers': {
        'telelog': {
            'handlers': ['telegram'],
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
telelog = logging.getLogger('telelog')
