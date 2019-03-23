"""
this is generator for ffmpeg
"""
import ffmpeg

class RenderGenerator:
    """
    instream outstream
    filter attribute
    """
    def __init__(self, instream: str, outstream: str):
        self.instream = instream
        self.outstream = outstream
        pass


