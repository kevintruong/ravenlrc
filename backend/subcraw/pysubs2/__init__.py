from .ssafile import SSAFile
from .ssaevent import SSAEvent
from .ssastyle import SSAStyle
from backend.subcraw.pysubs2 import cli, time
from .exceptions import *
from .common import Color, VERSION

#: Alias for :meth:`SSAFile.load()`.
load = SSAFile.load

#: Alias for :meth:`pysubs2.time.make_time()`.
make_time = time.make_time
