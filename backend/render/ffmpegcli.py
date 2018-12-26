from __future__ import unicode_literals, print_function

import json
import os
import subprocess
from enum import Enum
from pathlib import Path
import platform
import logging
import backend.yclogger

logger = logging.getLogger('backend')


class Coordinate(object):
    """

    """

    def __init__(self, x, y, w=0, h=0):
        """

        :param x:
        :param y:
        :param w:
        :param h:
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class FFmpegProfile(Enum):
    PROFILE_LOW = '640x480'
    PROFILE_FULLHD = '1920x1080'
    PROFILE_2K = '2048x1080'
    PROFILE_4K = '4096x2160'
    pass


class FfmpegCli(object):
    '''
    cli render for process video and audio
    '''

    def __add_system_prefix(self):
        curPlatform = platform.system()
        if curPlatform == "Windows":
            self.ffmpeg_cli.append('-hwaccel')
            self.ffmpeg_cli.append('d3d11va')
        elif curPlatform == "Linux":
            self.ffmpeg_cli.append('-hwaccel')
            self.ffmpeg_cli.append('vdpau')
        else:
            logger.debug('not support yet')

    def reset_ffmpeg_cmd(self):
        self.ffmpeg_cli.clear()
        # self.ffmpeg_cli = ['render', '-hide_banner', '-loglevel', 'panic', '-y']

        self.ffmpeg_cli = ['ffmpeg', '-y']
        # self.ffmpeg_cli = ['render', '-hide_banner', '-y']
        self.__add_system_prefix()

    def set_resolution(self, resolution: FFmpegProfile):
        self.default_resolution = resolution

    def __init__(self):
        self.ffmpeg_cli = []
        self.default_resolution = '1920x1080'
        self.default_bitrate = 8000000
        self.youtube_options = ["-movflags", "+faststart"]
        self.youtube_codec = ["-vcodec", "libx264", "-pix_fmt", "yuv420p"]
        self.ffmpeg_options = ["-threads", "8", "-y"]
        self.supperfast_profile = ["-preset", "ultrafast"]
        self.bitrate_configure = ["-b:v", "{}".format(self.default_bitrate)]
        self.copy_encode = ["-c", "copy"]
        self.reset_ffmpeg_cmd()
        self.__add_system_prefix()
        pass

    def _ffprobe_file_format(self, input: str):
        """

        :param input:
        :return:
        """
        # ffprobe - v quiet - print_format json - show_format
        ffproble_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', "-i",
                        "{}".format(input)]
        output, err = self.run_cmd(ffproble_cmd)
        data = json.loads(output)
        return data['format']

    def _ffmpeg_input(self, input: str):
        """
        add input to render command line
        :param input:
        :return:
        """
        FfmpegCli.check_file_exist(input)
        self.ffmpeg_cli.append("-i")
        self.ffmpeg_cli.append("{}".format(input))

    def _ffmpeg_input_filter_complex_prefix(self):
        """
        add filter_complex to render
        :return:
        """
        self.ffmpeg_cli.append("-filter_complex")

    def _ffmpeg_input_fill_cmd(self, cmd: str):
        self.ffmpeg_cli.append(cmd)

    def run_cmd(self, cmd: list):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = p.communicate(input)
        retcode = p.poll()
        if retcode:
            raise Exception('render', out, err)
        return out, err

    def run(self, cmd: list, output: str):
        cmd += self.bitrate_configure
        cmd.append(output)
        logger.debug(' '.join(map(str, cmd)))

        p = subprocess.Popen(cmd)
        out, err = p.communicate(input)
        retcode = p.poll()
        if retcode:
            raise Exception('render', out, err)
        return out, err

    def ffmpeg_cli_run(self, cmd: list, output: str, superfast=1, youtube=0):
        cmd += self.ffmpeg_options
        if superfast == 1:
            # cmd += self.supperfast_profile
            pass
        if youtube == 1:
            cmd += self.youtube_codec
            cmd += self.youtube_options
            cmd += self.bitrate_configure

        cmd.append(output)
        logger.debug(' '.join(map(str, cmd)))

        p = subprocess.Popen(cmd)
        out, err = p.communicate(input)
        retcode = p.poll()
        self.reset_ffmpeg_cmd()
        if retcode:
            self.reset_ffmpeg_cmd()
            raise Exception('render', out, err)
        return out, err

    @classmethod
    def check_file_exist(cls, inputfile: str):
        input_file = Path(inputfile)
        if not input_file.exists():
            logger.debug("not found file {}".format(inputfile))
            exit(-1)

    def get_media_time_length(self, media_file_name: str):
        FfmpegCli.check_file_exist(media_file_name)
        format = self._ffprobe_file_format(media_file_name)
        duration = int(round(float(format['duration'])))
        return duration

    def get_media_info(self, mediafile: str):
        FfmpegCli.check_file_exist(mediafile)
        format = self._ffprobe_file_format(mediafile)
        return format

    def create_media_file_from_img(self, input_img: str, time_length: int, output_video: str):
        '''
        render -loop 1 -i $input_img -c:v libx264 -t $length -pix_fmt yuvj422p -vf scale=$fullhd $output_mp4
        :param output_video:
        :param input_img:
        :param time_length:
        :return:
        '''
        FfmpegCli.check_file_exist(input_img)
        self._ffmpeg_input_fill_cmd('-loop')
        self._ffmpeg_input_fill_cmd('1')
        self._ffmpeg_input(input_img)
        self._ffmpeg_input_fill_cmd('-t')
        self._ffmpeg_input_fill_cmd("{}".format(time_length))
        self.ffmpeg_cli_run(self.ffmpeg_cli, output_video)

    def create_background_affect_with_length(self, input_bg, time_length: int, output_bg):
        '''
        the function will create an output backgound effect from input backround image
        render -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
        :param time_length:
        :param input_bg:
        :param output_bg:
        :return:
        '''
        FfmpegCli.check_file_exist(input_bg)
        self._ffmpeg_input_fill_cmd('-re')
        self._ffmpeg_input_fill_cmd('-stream_loop')
        self._ffmpeg_input_fill_cmd('-1')
        self._ffmpeg_input(input_bg)
        self._ffmpeg_input_fill_cmd('-t')
        self._ffmpeg_input_fill_cmd('{}'.format(time_length))
        # self._ffmpeg_input_fill_cmd('-c')
        # self._ffmpeg_input_fill_cmd('copy')
        self.ffmpeg_cli_run(self.ffmpeg_cli, output_bg)

        # ffmpeg_cmd = ["render", "-y", "-re", "-stream_loop", "-1", "-i", "{}".format(input_bg), "-t",
        #               "{}".format(time_length)]
        #
        # self.ffmpeg_cli_run(ffmpeg_cmd, output_bg)l l l l

    def scale_input(self, input_bg, resolution: str, output_bg):
        '''
        the function will create an output backgound effect from input backround image
        render -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
        :param time_length:
        :param input_bg:
        :param output_bg:
        :return:
        '''
        FfmpegCli.check_file_exist(input_bg)
        self._ffmpeg_input(input_bg)
        self._ffmpeg_input_filter_complex_prefix()
        cmd = 'scale={}'.format(resolution)
        self._ffmpeg_input_fill_cmd(cmd)
        self.ffmpeg_cli_run(self.ffmpeg_cli, output_bg)

        # ffmpeg_cmd = ["render", "-y", "-re", "-stream_loop", "-1", "-i", "{}".format(input_bg), "-t",
        #               "{}".format(time_length)]
        #
        # self.ffmpeg_cli_run(ffmpeg_cmd, output_bg)

    def adding_sub_to_video(self, input_sub: str, input_video: str, output_vid: str):
        '''
        ffmpeg_sub_cmd="f=$(pwd)/${input_sub}:force_style="
        ffmpeg_font_att="FontName=$input_font,FontSize=$font_size,PrimaryColour=&H${opacity}${font_colour_1},BorderStyle=0"
        ffmpeg_cmd=$(echo render -y -i ${input_vid} -vf subtitles='"'${ffmpeg_sub_cmd}"'"${ffmpeg_font_att}"'"'"':original_size=${FULLHD} ${output_mp4})
        echo ${ffmpeg_cmd} | bash

        render -y -i input.mp4 -vf subtitles="f=/mnt/775AD44933621551/Project/MMO/youtube/test.ass:force_style='FontName=UTM Bustamalaka,FontSi
        ze=10,OutlineColour=&H66000000,BorderStyle=3'":original_size=1920x1080 002.mp4
        :param input_sub:
        :param input_video:
        :param output_vid:
        :return:
        '''

        FfmpegCli.check_file_exist(input_sub)
        FfmpegCli.check_file_exist(input_video)
        self._ffmpeg_input(input_video)
        self._ffmpeg_input_filter_complex_prefix()
        # Replace back slash -> forward slash
        input_sub = input_sub.replace(os.sep, '/')
        newass = input_sub[:1] + "\\" + input_sub[1:]
        cmd = "subtitles=\\'{}\\'".format(newass)
        self._ffmpeg_input_fill_cmd(cmd)
        self._ffmpeg_input_fill_cmd('-shortest')
        self.ffmpeg_cli_run(self.ffmpeg_cli, output_vid)
        pass

    def add_affect_to_video(self, affect_vid: str, video: str, output: str, affectconf=50):
        """
        input_bgvid=$1
        input_blendvid=$2
        output_mp4=$3
        render -i ${input_bgvid} -i ${input_blendvid} -filter_complex \
                                     "[1:0]setdar=dar=0,format=rgba[a]; \
                                      [0:0]setdar=dar=0,format=rgba[b]; \
                                      [b][a]blend=all_mode='overlay':all_opacity=0.5" \
                                      $output_mp4
        :param output:
        :param affectconf:
        :param affect_vid:
        :param video:
        :return:
        """
        FfmpegCli.check_file_exist(affect_vid)
        FfmpegCli.check_file_exist(video)
        self._ffmpeg_input(affect_vid)
        self._ffmpeg_input(video)
        self._ffmpeg_input_filter_complex_prefix()
        opacity = float(affectconf / 100)
        filter_args = "[1:0]setdar=dar=0,format=rgba[a]; \
                       [0:0]setdar=dar=0,format=rgba[b]; \
                       [b][a]blend=all_mode='overlay':all_opacity={}".format(opacity)
        self._ffmpeg_input_fill_cmd(filter_args)
        # ffmpeg_cmd = ["render", "-y", "-i", "{}".format(video), "-i", "{}".format(bg_video), "-filter_complex",
        #               "{}".format(filter_args)]
        self.ffmpeg_cli_run(self.ffmpeg_cli, output)

    def mux_audio_to_video(self, input_vid: str, input_audio: str, output_vid: str):
        '''
        render -i ${input_vid} -i $input_aud -map 0:v -map 1:a -c copy -shortest ${output_mv}
        :param input_vid:
        :param input_audio:
        :param output_vid:
        :return:
        '''
        FfmpegCli.check_file_exist(input_vid)
        FfmpegCli.check_file_exist(input_audio)
        ffmpeg_cmd = ["render", "-y",
                      "-i", "{}".format(input_vid),
                      "-i", "{}".format(input_audio),
                      "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest"]
        self._ffmpeg_input_fill_cmd('-c')
        self._ffmpeg_input_fill_cmd('copy')
        self.ffmpeg_cli_run(ffmpeg_cmd, output_vid, superfast=1)

    def add_logo_to_bg_img(self, input_bg: str, input_logo: str, output: str,
                           coordinate=Coordinate(512, 512), transparent=0.9):
        """
        render -i small.mp4 -i avatar.png -filter_complex
                    "[1:v]format=argb,colorchannelmixer=aa=0.5[zork];
                    [0:v][zork]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"
                    -codec:a copy output.mp4

        :param output:
        :param transparent:
        :param input_bg:
        :param input_logo:
        :param coordinate:
        :return:
        """
        FfmpegCli.check_file_exist(input_bg)
        FfmpegCli.check_file_exist(input_logo)
        self._ffmpeg_input(input_bg)
        self._ffmpeg_input(input_logo)
        self._ffmpeg_input_filter_complex_prefix()
        filter = "[1:v]format=argb,colorchannelmixer=aa={}[zork];\
                    [0:v][zork]overlay={}:{}".format(transparent, coordinate.x, coordinate.y)
        self._ffmpeg_input_fill_cmd(filter)

        logger.debug('{}'.format(self.ffmpeg_cli))
        self.run(self.ffmpeg_cli, output)
        self.reset_ffmpeg_cmd()

    def add_affect_overlay_in_sub(self, input_src: str, affect: str, subframe: Coordinate,
                                  outdir=os.path.dirname(__file__)):
        """
        render -ss 00:01:00.680 -i "INPUT.mp4" -i overlay.apng -ss 00:00:10.000 -t 00:11:39.759
       -filter_complex "[0]crop=in_w-8:in_h-8[a];[a][1]overlay,scale=1280:-1"
       -c:a copy -c:v libx264 -preset slow -crf 25 "OUTPUT.mp4"
        crop the affect to subframe
        overlay affect to input_src with subframe coordinate
        :param outdir:
        :param input_src:
        :param affect:
        :type subframe: Coordinate
        :param subframe:
        :return:
        """
        self._ffmpeg_input(input_src)
        self._ffmpeg_input(affect)
        self._ffmpeg_input_filter_complex_prefix()
        #           "[1]lut=a=val*0.3[a];[0][a]overlay=0:0"
        # [b][a]blend=all_mode='overlay':all_opacity=0.3"
        filter = "[1:v]crop={}:{}:000:100[a];\
        [a]format=argb,colorchannelmixer=aa={}[zork];\
        [0:v][zork]overlay={}:{}".format(subframe.w, subframe.h, 0.9, subframe.x, subframe.y)
        # [0:v][zork]overlay={}:{}".format(subframe.w, subframe.h, 0.3, subframe.x, subframe.y)
        # filter = "[1]split=2[a][b];[a]alphaextract[alf];[0:v][alf]alphamerge"

        self._ffmpeg_input_fill_cmd(filter)

        logger.debug("{}".format(self.ffmpeg_cli))
        self.run(self.ffmpeg_cli, outdir)
        pass

    # parser = argparse.ArgumentParser(description='Get video information')
    # parser.add_argument('in_filename', help='Input filename')
    #
    # if __name__ == '__main__':
    #     args = parser.parse_args()
    # ffmpeg_cli = FffmpegCli()
    #     time_length = ffmpeg_cli.get_media_time_length(args.in_filename)
    #     logger.debug("time length " + str(time_length))
    # ffmpeg_cli.add_logo_to_bg_img(
    #     '/mnt/775AD44933621551/Project/MMO/youtube/Content/CoverImage/NhamMatThayMuaHe_Background.png',
    #     '/mnt/775AD44933621551/Project/MMO/youtube/Content/Titile/Xinloi.png', Coordinate(100, 100))
# ffmpeg_cli.add_affect_overlay_in_sub("/tmp/xin_loi_img.mp4",
#                                      "/mnt/775AD44933621551/Project/MMO/youtube/Content/bg_affect/test.gif",
#                                      subframe=Coordinate(000, 000, 1920, 1080))
#
# ffmpeg_cli.create_media_file_from_img(
#     "/mnt/775AD44933621551/Project/MMO/youtube/Content/CoverImage/NhamMatThayMuaHe_Background.png",
#     time_length, "/tmp/xin_loi_img.mp4")
# # ffmpeg_cli.create_background_affect_with_length(
# #     "/mnt/775AD44933621551/Project/MMO/youtube/Content/bg_affect/y73ofoao",
# #     time_length, "temp/xin_loi_bg.mp4")
# ffmpeg_cli.adding_sub_to_video("/mnt/775AD44933621551/Project/MMO/youtube/output_file.ass",
#                                "temp/xin_loi_img.mp4",
#                                "temp/xin_loi_sub.mp4"
#                                )
#
# ffmpeg_cli.mux_audio_to_video("temp/xin_loi_sub.mp4",
#                               "/mnt/775AD44933621551/Project/MMO/youtube/Content/Music/Nham_mat_thay_mua_he.mp3",
#                               "temp/xin_loi.mp4")
#
# ffmpeg_cli.add_affect_to_video(
#     "temp/xin_loi_bg.mp4",
#     "temp/xin_loi.mp4",
#     "xin_loi_final.mp4")
# try:
#     probe = render.probe(args.in_filename)
# except render.Error as e:
#     logger.debug(e.stderr, file=sys.stderr)
#     sys.exit(1)

# video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
# if video_stream is None:
#     logger.debug('No video stream found', file=sys.stderr)
#     sys.exit(1)
#
# width = int(video_stream['width'])
# height = int(video_stream['height'])
# # num_frames = int(video_stream['nb_frames'])
# logger.debug('width: {}'.format(width))
# logger.debug('height: {}'.format(height))
# logger.debug('num_frames: {}'.format(num_frames))
