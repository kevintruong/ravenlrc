from __future__ import unicode_literals

import subprocess
from urllib.parse import urlparse

from backend.TempFileMnger import *
from backend.ffmpeg.ffmpegcli import FFmpegProfile
from backend.subcraw import pylrc
from backend.subcraw.pysubs2 import *
from backend.subcraw.pysubs2.substation import ssa_rgb_to_color, color_to_ass_rgba

temp_dowload_dir = os.path.join(os.path.dirname(__file__), 'Download')
if not os.path.isdir(temp_dowload_dir):
    os.mkdir(temp_dowload_dir)


class textrefactor(object):
    """
    this is class for adding effect to a text line (ASSEvent)
    """

    def __init__(self, text: str, duration: int):
        self.text = text
        self.duration = duration
        self.df_alpha_1 = 0xff
        self.df_alpha_2 = 0x10
        self.df_plpha_3 = 0xff
        self.df_t1 = 0
        self.df_t2 = 0.30
        self.df_t3 = 0.50
        self.df_t4 = 0.20
        self.newtext = None

    def add_fade_effect(self):
        t1 = 0
        t2 = int(self.duration * self.df_t2)
        t3 = int(self.duration * self.df_t3)
        t4 = 5000
        fade_affect = "{{\\fade({},{},{},{},{},{},{})}}".format(self.df_alpha_1, self.df_alpha_2, self.df_plpha_3, t1,
                                                                t2, t3, t4)
        self.newtext = fade_affect + self.text
        pass

    def get_newtext(self):
        return self.newtext


class AssCustomizor(object):
    """
    this is the temple document for sub customizer
    """

    def __init__(self, this_subtile, framewidth=1920, frameheigh=1080):
        self.subs = this_subtile
        self.default_sub_width = 800
        self.setting_resolution(framewidth, frameheigh)
        self.default_fontsize = int(frameheigh * 5 / 100)

    def setting_fonts(self, fontname: str, size=None):
        '@:type fontname: str'

        default_style = self.subs.styles["Default"]
        default_style.italic = True
        default_style.fontname = fontname
        if size is None:
            default_style.fontsize = self.default_fontsize
        else:
            default_style.fontsize = size
        pass

    def setting_margin_val(self, x=0, y=0, w=300, h=200):
        """
           this function will setting the margin value of subtitle field
           for exampel : marginl the left margin offset from screen
                         marginr the right margin offset from right side tof screen
                         marginv the bottom margin offset from bottom side of screen
           will fixed the default space of subtitle size width is 500 pixel
           then the calculate for marginl,marginr,marginv should be
           if l > r => marginr = r, marginl= marginl - marginr - default_width(500)
           if r > l => marginl = l, marginr =marginr -marginl -default_width (500)
           marginv = v retangle (x,y,w,h)
            convert to (x,y) format =>  marginl =x
                                        marginr =x + w
                                        marginv = screen_heigh - y - h
        :param x:
        :param y:
        :param w:
        :param h:
        :return:
        """
        sub_info = self.subs.info
        resX = sub_info["PlayResX"]
        resY = sub_info["PlayResY"]

        default_style = self.subs.styles["Default"]
        default_style.marginr = resX - (x + w)
        default_style.marginl = x
        default_style.marginv = resY - (y + h)

    def setting_resolution(self, x, y):
        sub_info = self.subs.info
        sub_info["PlayResX"] = x
        sub_info["PlayResY"] = y

    def setting_primary_colour(self, colorcode: int):
        '''
        setting primary colour: Input is hex code of rgb, need to convert to brg. Is mean revert the order
        :param colorcode: hex code of rgb colour
        :return:
        '''
        color = ssa_rgb_to_color(colorcode)
        default_style = self.subs.styles["Default"]
        default_style.primarycolor = color_to_ass_rgba(color)

    def add_fad_affect_to_sub(self):
        """
        add fad affect to subtitle. For example:
        1.
        :return:
        """

        for line in self.subs:
            newtext = textrefactor(line.plaintext, line.duration)
            newtext.add_fade_effect()
            line.text = newtext.get_newtext()
        pass

    @classmethod
    def convert_to_ass(cls, srtfile: str, assfile: str):
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "panic", "-i", "{}".format(srtfile), "{}".format(assfile), "-y"]
        p = subprocess.Popen(cmd)
        out, err = p.communicate(input)
        retcode = p.poll()
        if retcode:
            raise Exception('ffmpeg', out, err)
        return assfile


def convert_lrf_to_ass(inputlrf: str, assoutput="/tmp/test.ass"):
    lrc_file = open(inputlrf)
    lrc_string = ''.join(lrc_file.readlines())
    lrc_file.close()
    subs = pylrc.parse(lrc_string)
    srt = subs.toSRT()  # convert lrc to srt string
    srtfile = subs.save_to_file('/tmp/output_test.srt')
    outputfile = AssCustomizor.convert_to_ass(srtfile, assoutput)
    return outputfile


def lrf_to_ass(lrccontent: str, output=os.path.join(temp_dowload_dir, "test.ass")):
    subs = pylrc.parse(lrccontent)
    srt = subs.toSRT()  # convert lrc to srt string
    srtfile = subs.save_to_file(os.path.join(temp_dowload_dir, 'output_test.srt'))
    outputfile = AssCustomizor.convert_to_ass(srtfile, output)
    return outputfile


class SubRectangle:
    def __init__(self, subrect: list):
        self.x = subrect[0]
        self.y = subrect[1]
        self.w = subrect[2]
        self.h = subrect[3]


class SubtitleInfo:
    def __init__(self, subinfo: dict):
        self.rectangle: SubRectangle = SubRectangle(subinfo['rectangle'])
        self.fontname = subinfo['fontname']
        self.fontcolor = subinfo['fontcolor']
        self.fontsize = subinfo['fontsize']

    def scale(self, resolution: FFmpegProfile):
        if resolution == FFmpegProfile.PROFILE_LOW:
            pass
        elif resolution == FFmpegProfile.PROFILE_2K:
            pass
        elif resolution == FFmpegProfile.PROFILE_4K:
            pass


def create_ass(lrcfile: str, output: str,
               subinfo: SubtitleInfo,
               resolution=None):
    with open(lrcfile, 'r', encoding='utf-8') as lrcfd:
        lrccontent = lrcfd.read()
        create_ass_subtitle(lrccontent, output, subinfo, resolution)


def create_ass_subtitle(lrccontent: str,
                        output: str,
                        subinfo: SubtitleInfo,
                        resolution=None):
    if resolution is None:
        res = [1920, 1080]
    elif resolution == FFmpegProfile.PROFILE_LOW:
        res = [640, 480]
    elif resolution == FFmpegProfile.PROFILE_FULLHD:
        res = [1920, 1080]
    else:
        res = [1920, 1080]

    sub_rectangle = subinfo.rectangle
    subcorlor = subinfo.fontcolor
    font_name = subinfo.fontname
    font_size = subinfo.fontsize

    # def create_ass_subtitile(inputfile: str,
    #                          output: str,
    #                          sub_rectangle: SubRectangle,
    #                          subcorlor=0x018CA7,
    #                          font_name="SVN-Futura",
    #                          font_size=None,
    #                          resolution=None):
    """

    :type inputfile: str input file lrf
    """
    asstempfile = AssTempFile().getfullpath()
    outputfile = lrf_to_ass(lrccontent, asstempfile)
    subs = SSAFile.load(outputfile, encoding='utf-8')  # create ass file
    sub_customizer = AssCustomizor(subs, res[0], res[1])
    sub_customizer.setting_fonts(font_name, font_size)
    sub_customizer.setting_margin_val(sub_rectangle.x, sub_rectangle.y, sub_rectangle.w, sub_rectangle.h)
    sub_customizer.setting_primary_colour(subcorlor)
    sub_customizer.add_fad_affect_to_sub()
    sub_customizer.subs.save(output)
    pass


def get_url(url: str):
    parse = urlparse(url)
    html_file = os.path.basename(parse)
    lyricfile = os.path.splitext(html_file)[0]
    return lyricfile + ".ass"


def create_ass_sub(url: str, output: str, subinfo: SubtitleInfo,
                   resolution=[1920, 1080]):
    """
    create ass subtitle for
    :param subinfo:
    :param resolution:
    :param url:
    :param output:
    :return:
    """
    # lrc_temp = LrcTempFile().getfullpath()
    from backend.subcraw.subcrawler import get_sub_from_url
    lrc_content = get_sub_from_url(url)
    # crawl_lyric(url, lrc_temp)
    create_ass_subtitle(lrc_content, output, subinfo, resolution)
    return output

# create_ass_subtitile(
#     "/mnt/775AD44933621551/Project/MMO/youtube/Content/Lyric/Nham_mat_thay_mua_he.lrc",
#     "/mnt/775AD44933621551/Project/MMO/youtube/Content/Ass/Nham_mat_thay_mua_he.ass")
# subs = load(outputfile, encoding='utf-8')
# sub_customizer = subcustomizor(subs)
# sub_customizer.setting_fonts("SVN-Futura", 64)
# sub_customizer.setting_resolution(1920, 1080)
# sub_customizer.setting_margin_val(200, 70)
# sub_customizer.setting_primary_colour(0x018CA7)
# sub_customizer.add_fad_affect_to_sub()
# sub_customizer.subs.save("output_file.ass")

# my_style = subs.styles["Default"].copy()
# my_style.italic = True
# my_style.fontname = "UTM Bustamalaka"
# subs.styles["Default"] = my_style
# sub_info = subs.info
# sub_info["PlayResX"] = 1920
# sub_info["PlayResY"] = 1080
# subs.save("change_font_xinloi.ass")
