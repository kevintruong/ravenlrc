import ast
import inspect
import shutil
import tempfile

import click
from backend.ffmpeg.ffmpegcli import FfmpegCli, Coordinate
from backend.subeffect.subcrawler import *
import backend.YTLogger
import logging
from backend.TempFileMnger import *

logger = logging.getLogger('backend')


def set_return_value(value):
    os.environ['RETURN_VALUE'] = str(value)


def get_return_value():
    return os.environ['RETURN_VALUE']


class BuildType(IntEnum):
    BUILD_PREVIEW = 0x00
    BUILD_RELEASE = 0x01


@click.group()
def cli():
    pass


#
#
# @cli.command('downloadcontent')
# @click.argument('quality', type=str)
# @click.argument('ncturl', required=True)
# @click.argument('outdir')
# def download_content_from_nct(quality: str, ncturl: str, outdir: str):
#     """
#     Download content from nhaccuatui with audio quality defined
#     to @outdir directory path \n
#     :param quality: integer 1 128kbps 2 320kbps 3 lossless \n
#     :param ncturl: nhaccuatui ulr \n
#     :param outdir: save file to dir \n
#     """
#     audio = AudioQuanlity(int(quality))
#     logger.debug("{} {} {}".format(audio, ncturl, outdir))
#     downloadfile = download_mp3_file(ncturl, audio, outdir)
#     set_return_value(downloadfile)
#     click.echo(downloadfile)
#
#
# @cli.command('getsub')
# @click.argument('ncturl', required=True)
# @click.argument('savefile', required=True)
# @click.argument('subfont')
# @click.argument('subcolor')
# @click.option('--subrect', default=[], help='enter list of subrectangle. Example: --subrect x,y,w,h')
# def get_sub_nct(ncturl, savefile, subfont, subcolor, subrect=None):
#     """
#     get lyric file from nhaccuatui to @savefile. In @savefile will configure font by subfont, color by subcolor
#     and possition of subtitle by subrect (x,y,w,h) \n
#
#     :param ncturl: \b
#     :param savefile: \n
#     :param subfont: \n
#     :param subcolor: \n
#     :param subrect: \n
#     """
#     sub_rect = ast.literal_eval(subrect)
#     create_ass_sub(ncturl, savefile, fontname=subfont, subcolor=int(subcolor, 0),
#                    sub_rect=SubRectangle(sub_rect[0], sub_rect[1], sub_rect[2], sub_rect[3]))
#     set_return_value(savefile)
#
#
# @cli.command('medialength')
# @click.argument('mediafile', required=True)
# def get_media_length(mediafile):
#     ffmpeg = FfmpegCli()
#     timelength = ffmpeg.get_media_time_length(mediafile)
#     set_return_value(timelength)
#
#
# @cli.command('addsub2mv')
# @click.argument('subfile')
# @click.argument('mvfile')
# @click.argument('output')
# def adding_sub_to_mv(subfile, mvfile, output):
#     ffmpeg = FfmpegCli()
#     ffmpeg.adding_sub_to_video(subfile, mvfile, output)
#     set_return_value(output)
#
#
# @cli.command('createytmv')
# @click.argument('audiofile', required=True)
# @click.argument('bgimgfile', required=True)
# @click.argument('titleimg', required=True)
# @click.option('--titlecoordinate', help='title coordinate: --titlecoordinate x.y')
# @click.argument('subfile', required=True)
# @click.argument('affectfile')
# @click.argument('affconfig', required=True)
# @click.argument('outputmv', required=True)
# def create_youtube_mv(audiofile,  # Audio file
#                       bgimgfile,  # backgground file
#                       titleimg, titlecoordinate,  # title image file and title configure
#                       subfile,  # subtitle file
#                       affectfile, affconfig,  # affect file and affect configure
#                       outputmv):  # output file
#     """
#     create youtube MV from resource file  \n
#     :param audiofile: file path to audio file  \n
#     :param bgimgfile: background image file (file path) \n
#     :param titleimg:  title image file path \n
#     :param titlecoordinate: coordinate of title x,y \n
#     :param subfile:  subtitle file  file path \n
#     :param affectfile:  affect file file path \n
#     :param affconfig:  affect configure  \n
#     :param outputmv:  output mv  \n
#     :return:
#     """
#     if not os.path.isfile(audiofile):
#         click.echo("{} not found".format(audiofile))
#         exit(-1)
#     if not os.path.isfile(bgimgfile):
#         click.echo("{} not found".format(bgimgfile))
#         exit(-1)
#     if not os.path.isfile(titleimg):
#         click.echo("{} not found".format(titleimg))
#         exit(-1)
#     if not os.path.isfile(subfile):
#         click.echo("{} not found".format(affectfile))
#     bg_vid = MvTempFile().getfullpath()
#     vidsubmv = MvTempFile().getfullpath()
#     addedtitleimg = PngTempFile().getfullpath()
#     affectmv = MvTempFile().getfullpath()
#     affectfull = MvTempFile().getfullpath()
#
#     sub_rect = ast.literal_eval(titlecoordinate)
#     ffmpeg = FfmpegCli()
#     timelength = ffmpeg.get_media_time_length(audiofile)
#     ffmpeg.add_logo_to_bg_img(bgimgfile, titleimg, addedtitleimg, Coordinate(sub_rect[0], sub_rect[1]))
#     ffmpeg.create_media_file_from_img(addedtitleimg, timelength, bg_vid)
#     ffmpeg.create_background_affect_with_length(affectfile, timelength, affectfull)
#     ffmpeg.add_affect_to_video(bg_vid, affectfull, affectmv, int(affconfig, 10))
#     ffmpeg.adding_sub_to_video(subfile, affectmv, vidsubmv)
#     ffmpeg.mux_audio_to_video(vidsubmv, audiofile, outputmv)
#
#     pass


@cli.command('build')
@click.argument('type', type=int, required=True)
@click.option('--bg_id', type=str, help='background id')
@click.option('--affect_id', help='affect id')
@click.option('--affect_conf', type=int, help='affect configure')
@click.option('--song_id', help='song id')
@click.argument('output_file', required=True)
def build_mv(type, bg_id, affect_id, affect_conf, song_id, output_file):
    """
    :param type:
    :param bg_id:
    :param affect_id:
    :param affect_conf:
    :param song_id:
    :param output_file:
    """
    logger.debug("build_mv " + str(locals()))
    build_type = BuildType(type)
    if build_type == BuildType.BUILD_PREVIEW:
        logger.debug("{}".format(build_type.name))
    elif build_type == BuildType.BUILD_RELEASE:
        logger.debug("{}".format(build_type.name))
    # get_song(song_id)

    create_ass_subtitile(ncturl, savefile, fontname=subfont, subcolor=int(subcolor, 0),
               sub_rect=SubRectangle(sub_rect[0], sub_rect[1], sub_rect[2], sub_rect[3]))
    set_return_value(savefile)
#
    pass


@cli.command('build_mv_use_template')
@click.argument('type', type=int, required=True)
@click.option('--template_id', type=str, help='template id')
@click.option('--song_id', help='song id')
@click.argument('output_file', required=True)
def build_mv_use_template(type, template_id, song_id, output_file):
    logger.debug("build_mv_with_template" + str(locals()))
    build_type = BuildType(type)
    if build_type == BuildType.BUILD_PREVIEW:
        logger.debug("{}".format(build_type.name))
    elif build_type == BuildType.BUILD_RELEASE:
        logger.debug("{}".format(build_type.name))
    pass


@cli.command('build_template')
@click.argument('type', type=int, required=True)
@click.option('--background_id', type=str, help='template id')
@click.option('--affect_id', help='song id')
@click.option('--affect_conf', type=int, help='affect configure')
@click.argument('output_file', required=True)
def build_template(type, background_id, affect_id, affect_conf, output_file):
    logger.debug("build_mv_with_template" + str(locals()))
    build_type = BuildType(type)
    if build_type == BuildType.BUILD_PREVIEW:
        logger.debug("{}".format(build_type.name))
    elif build_type == BuildType.BUILD_RELEASE:
        logger.debug("{}".format(build_type.name))
    pass


@cli.command('nct_crawl')
@click.argument('ncturl', required=True)
@click.option('--audio_quality', type=int)
@click.option('--audio_output', help="crawl nct audio file ")
@click.option('--lyric_output', help="output lyric file")
def nct_crawl(ncturl, audio_quality, audio_output, lyric_output):
    """

    :param ncturl: nhaccuatui url (link music single) \n
    :param audio_quality:  (integer 1-4) \n
    :param audio_output:    string file path audio \n
    :param lyric_output:    string lyric output \n
    """
    if audio_quality:
        audioQuality = AudioQuanlity(audio_quality)
        audiFile = download_mp3_file(ncturl, audioQuality)
        shutil.copy(audiFile, audio_output)
    if lyric_output:
        crawl_lyric(ncturl, lyric_output)
    logger.debug("nct_crawl" + str(locals()))
    pass


if __name__ == '__main__':
    cli()
    pass
