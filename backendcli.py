import ast
import tempfile

import click
from backend.ffmpeg.ffmpegcli import FfmpegCli, Coordinate
from backend.subcraw.subcrawler import *
import backend.YTLogger
import logging
from backend.TempFileMnger import *

logger = logging.getLogger('kendebug')


def set_return_value(value):
    os.environ['RETURN_VALUE'] = str(value)


def get_return_value():
    return os.environ['RETURN_VALUE']


@click.group()
def cli():
    pass


@cli.command('downloadcontent')
@click.argument('quality', type=str)
@click.argument('ncturl', required=True)
@click.argument('outdir')
def download_content_from_nct(quality: str, ncturl: str, outdir: str):
    """
    Download content from nhaccuatui with audio quality defined
    to @outdir directory path \n
    :param quality: integer 1 128kbps 2 320kbps 3 lossless \n
    :param ncturl: nhaccuatui ulr \n
    :param outdir: save file to dir \n
    """
    audio = AudioQuanlity(int(quality))
    logger.debug("{} {} {}".format(audio, ncturl, outdir))
    downloadfile = download_mp3_file(ncturl, audio, outdir)
    set_return_value(downloadfile)
    click.echo(downloadfile)


@cli.command('getsub')
@click.argument('ncturl', required=True)
@click.argument('savefile', required=True)
@click.argument('subfont')
@click.argument('subcolor')
@click.option('--subrect', default=[], help='enter list of subrectangle. Example: --subrect x,y,w,h')
def get_sub_nct(ncturl, savefile, subfont, subcolor, subrect=None):
    """
    get lyric file from nhaccuatui to @savefile. In @savefile will configure font by subfont, color by subcolor
    and possition of subtitle by subrect (x,y,w,h) \n

    :param ncturl: \b
    :param savefile: \n
    :param subfont: \n
    :param subcolor: \n
    :param subrect: \n
    """
    sub_rect = ast.literal_eval(subrect)
    create_ass_sub(ncturl, savefile, fontname=subfont, subcolor=int(subcolor, 0),
                   sub_rect=SubRectangle(sub_rect[0], sub_rect[1], sub_rect[2], sub_rect[3]))
    set_return_value(savefile)


@cli.command('medialength')
@click.argument('mediafile', required=True)
def get_media_length(mediafile):
    ffmpeg = FfmpegCli()
    timelength = ffmpeg.get_media_time_length(mediafile)
    set_return_value(timelength)


@cli.command('addsub2mv')
@click.argument('subfile')
@click.argument('mvfile')
@click.argument('output')
def adding_sub_to_mv(subfile, mvfile, output):
    ffmpeg = FfmpegCli()
    ffmpeg.adding_sub_to_video(subfile, mvfile, output)
    set_return_value(output)


@cli.command('createytmv')
@click.argument('audiofile', required=True)
@click.argument('bgimgfile', required=True)
@click.argument('titleimg', required=True)
@click.option('--titlecoordinate', help='title coordinate: --titlecoordinate x.y')
@click.argument('subfile', required=True)
@click.argument('affectfile')
@click.argument('affconfig', required=True)
@click.argument('outputmv', required=True)
def create_youtube_mv(audiofile,  # Audio file
                      bgimgfile,  # backgground file
                      titleimg, titlecoordinate,  # title image file and title configure
                      subfile,  # subtitle file
                      affectfile, affconfig,  # affect file and affect configure
                      outputmv):  # output file
    """
    create youtube MV from resource file  \n
    :param audiofile: file path to audio file  \n
    :param bgimgfile: background image file (file path) \n
    :param titleimg:  title image file path \n
    :param titlecoordinate: coordinate of title x,y \n
    :param subfile:  subtitle file  file path \n
    :param affectfile:  affect file file path \n
    :param affconfig:  affect configure  \n
    :param outputmv:  output mv  \n
    :return:
    """
    if not os.path.isfile(audiofile):
        click.echo("{} not found".format(audiofile))
        exit(-1)
    if not os.path.isfile(bgimgfile):
        click.echo("{} not found".format(bgimgfile))
        exit(-1)
    if not os.path.isfile(titleimg):
        click.echo("{} not found".format(titleimg))
        exit(-1)
    if not os.path.isfile(subfile):
        click.echo("{} not found".format(affectfile))
    bg_vid = MvTempFile().getfullpath()
    vidsubmv = MvTempFile().getfullpath()
    addedtitleimg = PngTempFile().getfullpath()
    affectmv = MvTempFile().getfullpath()
    affectfull = MvTempFile().getfullpath()

    sub_rect = ast.literal_eval(titlecoordinate)
    ffmpeg = FfmpegCli()
    timelength = ffmpeg.get_media_time_length(audiofile)
    ffmpeg.add_logo_to_bg_img(bgimgfile, titleimg, addedtitleimg, Coordinate(sub_rect[0], sub_rect[1]))
    ffmpeg.create_media_file_from_img(addedtitleimg, timelength, bg_vid)
    ffmpeg.create_background_affect_with_length(affectfile, timelength, affectfull)
    ffmpeg.add_affect_to_video(bg_vid, affectfull, affectmv, int(affconfig, 10))
    ffmpeg.adding_sub_to_video(subfile, affectmv, vidsubmv)
    ffmpeg.mux_audio_to_video(vidsubmv, audiofile, outputmv)

    pass


@cli.command('hello_nodejs')
def hello_nodejs():
    logger.debug("hello world")
    click.echo("hello node js")


if __name__ == '__main__':
    cli()
    pass
