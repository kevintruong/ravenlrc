# TODO
# ''' - Option args
# '''
#
#

import ast
import click
from backend.ffmpeg.ffmpegcli import FfmpegCli
from backend.subcraw.subcrawler import *


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
    audio = AudioQuanlity(int(quality))
    downloadfile = download_mp3_file(ncturl, audio, outdir)
    set_return_value(downloadfile)


@cli.command('getsub')
@click.argument('ncturl', required=True)
@click.argument('savefile', required=True)
@click.argument('subfont')
@click.argument('subcolor')
@click.option('--subrect', default=[], help='enter list of subrectangle. Example: --subrect "[x,y,w,h]')
def get_sub_nct(ncturl, savefile, subfont, subcolor, subrect):
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


if __name__ == '__main__':
    cli()
    pass
