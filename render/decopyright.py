class DeCopyright:
    def __init__(self, mediafile):
        self.media_file = mediafile

    def run(self):
        # ffmpeg -y -i input.mp4 -af "[0:a]volume=1.5" -filter_complex "[0:v]boxblur=1:2"
        # -vcodec libx264  -pix_fmt yuv420p -r 30 -g 60 -b:v 1400k -profile:v main
        # -level 3.1 -acodec libmp3lame -b:a 128k -ar 44100
        # -metadata title="" -metadata artist="" -metadata album_artist="" -metadata album="" -metadata date=""
        # -metadata track="" -metadata genre="" -metadata publisher="" -metadata encoded_by="" -metadata copyright=""
        # -metadata composer="" -metadata performer="" -metadata TIT1="" -metadata TIT3="" -metadata disc=""
        # -metadata TKEY="" -metadata TBPM="" -metadata language="eng" -metadata encoder="" -threads 0 -preset
        # superfast "output_px3.mp4"

        pass
