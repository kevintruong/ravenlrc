from tempfile import *
import os

cur_dir = os.path.dirname(__file__)
temp_dir = os.path.join(cur_dir, 'tmp')
if not os.path.isdir(temp_dir):
    os.mkdir(temp_dir)


class YtTempFile:
    tempfilelst = []

    def __init__(self, pre, sub, autodel=False) -> None:
        self.tempfile = NamedTemporaryFile(prefix=pre, suffix=sub, delete=autodel, dir=temp_dir)
        YtTempFile.tempfilelst.append(self)
        self.tempfile.close()

    def getfullpath(self):
        return self.tempfile.name

    def file_delete(self):
        self.tempfile.delete()

    @classmethod
    def list_all_file(cls):
        for file in cls.tempfilelst:
            print("{}".format(file.getfullpath()))

    @classmethod
    def delete_all(cls):
        for file in cls.tempfilelst:
            os.remove(file.getfullpath())


class MvTempFile(YtTempFile):

    def __init__(self, pre='mv_', sub=".mp4", autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class BgMvTemplateFile(YtTempFile):
    def __init__(self, pre='bgmv_', sub=".mp4", autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class AffMvTemplateFile(YtTempFile):
    def __init__(self, pre='affmv_', sub=".mp4", autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class PngTempFile(YtTempFile):

    def __init__(self, pre='img_', sub='.png', autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class JpegTempFile(YtTempFile):

    def __init__(self, pre='img_', sub='.jpg', autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class AssTempFile(YtTempFile):
    def __init__(self, pre='sub', sub='.ass', autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class LrcTempFile(YtTempFile):
    def __init__(self, pre='sub', sub='.lrc', autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class SrtTempfile(YtTempFile):

    def __init__(self, pre='sub', sub='.srt', autodel=False) -> None:
        super().__init__(pre, sub, autodel)


class Mp3TempFile(YtTempFile):
    def __init__(self, pre='audio', sub='.mp3', autodel=False) -> None:
        super().__init__(pre, sub, autodel)