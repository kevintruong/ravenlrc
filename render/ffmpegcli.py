from __future__ import unicode_literals, print_function

import json
import os
import subprocess
from enum import Enum
from pathlib import Path
import platform
import logging

import ffmpeg
import ffmpegbin.ffmpegbin

ffmpegpath = os.path.join(ffmpegbin.ffmpegbin.ffmpegpath, 'ffmpeg')
ffprobepath = os.path.join(ffmpegbin.ffmpegbin.ffmpegpath, 'ffprobe')
# from backend.render.type import Size, Position
import psutil as psutil

logger = logging.getLogger('backend')
cpucount = psutil.cpu_count()


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


class Resolution:
    def __init__(self, res: str):
        res_x, res_y = res.split('x')
        self.res_x = int(res_x)
        self.res_y = int(res_y)


class FFmpegProfile(Enum):
    PROFILE_LOW = '1024x576'
    PROFILE_MEDIUM = '1280x720'
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
            self.ffmpeg_cli.append('dxva2')
        elif curPlatform == "Linux":
            pass
            # self.ffmpeg_cli.append('-hwaccel')
            # self.ffmpeg_cli.append('vdpau')
        else:
            logger.debug('not support yet')

    def reset_ffmpeg_cmd(self):
        self.ffmpeg_cli.clear()
        # self.ffmpeg_cli = ['render', '-hide_banner', '-loglevel', 'panic', '-y']

        # self.ffmpeg_cli = ['ffmpeg', '-y']
        self.ffmpeg_cli = ['{}'.format(ffmpegpath), '-hide_banner', '-y']
        self.__add_system_prefix()

    def __init__(self):
        # TODO print(os.cpu_count()) find cpu count
        self.ffmpeg_cli = []
        self.default_bitrate = 8000000
        self.youtube_options = ["-movflags", "+faststart"]
        self.youtube_codec = ["-vcodec", "libx264", "-pix_fmt", "yuv420p"]
        self.ffmpeg_options = ["-threads", "8", "-y"]
        self.supperfast_profile = ["-preset", "ultrafast"]
        self.bitrate_configure = ["-b:v", "{}".format(self.default_bitrate)]
        self.copy_encode = ["-c", "copy"]
        self.reset_ffmpeg_cmd()
        self.__add_system_prefix()
        self.ffmpegpath = os.path.join(ffmpegbin.ffmpegbin.ffmpegpath, 'ffmpeg')
        pass

    def _ffprobe_file_format(self, input: str):
        """

        :param input:
        :return:
        """
        # ffprobe - v quiet - print_format json - show_format
        ffproble_cmd = ['{}'.format(ffprobepath), '-v', 'quiet', '-print_format', 'json', '-show_format',
                        '-show_streams', "-i",
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
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate(input)
        retcode = p.poll()
        if retcode:
            raise Exception('render', out, err)
        return out, err

    def run(self, cmd: list, output: str):
        cmd += self.bitrate_configure
        cmd.append(output)
        logger.debug(' '.join(map(str, cmd)))
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate(input)
        retcode = p.poll()
        if retcode:
            raise Exception('ffmpeg', err)
        return out, err

    def ffmpeg_cli_run(self, cmd: list, output: str, superfast=1, youtube=0):
        global out, err
        cmd += self.ffmpeg_options
        if superfast == 1:
            cmd += self.supperfast_profile
            pass
        if youtube == 1:
            cmd += self.youtube_codec
            cmd += self.youtube_options
            cmd += self.bitrate_configure

        cmd.append(output)
        # print(' '.join(cmd))
        try:
            p = subprocess.Popen(cmd,
                                 # stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, err = p.communicate(input)
            retcode = p.poll()
            self.reset_ffmpeg_cmd()
            print("ffmpeg return code {}".format(retcode))
            if retcode:
                self.reset_ffmpeg_cmd()
                raise Exception('ffmpeg', out, err)
            return out, err
        except Exception as e:
            os.remove(output)
            raise Exception('ffmpeg', out, err)

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
        try:
            (
                ffmpeg.input(input_img, loop=1)
                    .output(output_video, t=time_length, framerate=25)
                    .run(cmd=ffmpegpath, overwrite_output=True)
            )
        except Exception as exp:
            os.remove(output_video)
            raise exp

    def create_background_affect_with_length(self, input_bg, time_length: int, output):
        '''
        the function will create an output backgound effect from input backround image
        render -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
        :param time_length:
        :param input_bg:
        :param output:
        :return:
        '''
        # loopcount = int(time_length / bg_timeleng) + 1
        try:
            FfmpegCli.check_file_exist(input_bg)
            (
                ffmpeg.input(input_bg, stream_loop=-1)
                    .output(output, t=time_length, framerate=25, c='copy')
                    .run(cmd=ffmpegpath, overwrite_output=True)
            )
        except Exception as exp:
            os.remove(output)
            raise exp
        # self._ffmpeg_input_fill_cmd('-re')
        # self._ffmpeg_input_fill_cmd('-stream_loop')
        # self._ffmpeg_input_fill_cmd('{}'.format(-1))
        # self._ffmpeg_input(input_bg)
        # self._ffmpeg_input_fill_cmd('-t')
        # self._ffmpeg_input_fill_cmd('{}'.format(time_length))
        # self._ffmpeg_input_fill_cmd('-c')
        # self._ffmpeg_input_fill_cmd('copy')
        # self.ffmpeg_cli_run(self.ffmpeg_cli, output_bg)

        # ffmpeg_cmd = ["render", "-y", "-re", "-stream_loop", "-1", "-i", "{}".format(input_bg), "-t",
        #               "{}".format(time_length)]
        #
        # self.ffmpeg_cli_run(ffmpeg_cmd, output_bg)l l l l

    def scale_effect_vid(self, input_effect, resolution, output):
        """
        ffmpeg -i <INPUT_FILE> -vf scale=720:540 -c:v <Video_Codec> <OUTPUT_FILE>
        :param input_effect:
        :param resolution:
        :param output:
        :return:
        """
        from render.type import Size
        resolution: Size
        try:
            FfmpegCli.check_file_exist(input_effect)
            (
                ffmpeg.input(input_effect)
                    .filter('scale', resolution.width, resolution.height)
                    .output(output, framerate=25, vcodec='png')
                    .run(cmd=ffmpegpath, overwrite_output=True)
            )
        except Exception as exp:
            os.remove(output)
            raise exp
        # self._ffmpeg_input(input_effect)
        # self._ffmpeg_input_filter_complex_prefix()
        # cmd = 'scale={}'.format(resolution)
        # self._ffmpeg_input_fill_cmd(cmd)
        # self._ffmpeg_input_fill_cmd('-c:v')
        # self._ffmpeg_input_fill_cmd('png')
        # self.ffmpeg_cli_run(self.ffmpeg_cli, output_effect)
        pass

    def scale_img_by_width_height(self, input_bg, resolution, output):
        '''
        the function will create an output backgound vid from input backround image
        render -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
        :param time_length:
        :param input_bg:
        :param output:
        :return:
        '''
        from render.type import Size
        resolution: Size
        try:
            FfmpegCli.check_file_exist(input_bg)
            self._ffmpeg_input(input_bg)
            self._ffmpeg_input_filter_complex_prefix()
            cmd = 'scale={}:{}'.format(resolution.width, resolution.height)
            self._ffmpeg_input_fill_cmd(cmd)
            self.ffmpeg_cli_run(self.ffmpeg_cli, output)
        except Exception as exp:
            os.remove(output)
            raise exp

    def scale_video_by_width_height(self, input_bg, resolution, output_bg, timelength=90):
        '''
        the function will create an output backgound vid from input backround image
        render -re -stream_loop -1 -i ${input_bgVid} -c copy -y -t ${input_length} ${output_vid}
        :param resolution:
        :param input_bg:
        :param output_bg:
        :return:
        '''
        from render.type import Size
        resolution: Size
        try:
            FfmpegCli.check_file_exist(input_bg)
            (
                ffmpeg.input(input_bg)
                    .filter('scale', resolution.width, -1)
                    .output(output_bg, framerate=25, vcodec='png', t=timelength)
                    .global_args('-shortest')
                    .run(cmd=ffmpegpath, overwrite_output=True)
            )
        except Exception as exp:
            os.remove(output_bg)
            raise exp

        # FfmpegCli.check_file_exist(input_bg)
        # self._ffmpeg_input(input_bg)
        # self._ffmpeg_input_filter_complex_prefix()
        # cmd = 'scale={}:-1'.format(resolution.width, resolution.height)
        # self._ffmpeg_input_fill_cmd(cmd)
        # self._ffmpeg_input_fill_cmd('-c:v')
        # self._ffmpeg_input_fill_cmd('png')
        # self.ffmpeg_cli_run(self.ffmpeg_cli, output_bg)

        # ffmpeg_cmd = ["render", "-y", "-re", "-stream_loop", "-1", "-i", "{}".format(input_bg), "-t",
        #               "{}".format(time_length)]
        #
        # self.ffmpeg_cli_run(ffmpeg_cmd, output_bg)

    def adding_sub_to_video(self, input_sub: str, input_video: str, output_vid: str, timelength=90):
        """
        ffmpeg_sub_cmd="f=$(pwd)/${input_sub}:force_style="
        ffmpeg_font_att="FontName=$input_font,FontSize=$font_size,PrimaryColour=&H${opacity}${font_colour_1},BorderStyle=0"
        ffmpeg_cmd=$(echo render -y -i ${input_vid} -vf subtitles='"'${ffmpeg_sub_cmd}"'"${ffmpeg_font_att}"'"'"':original_size=${FULLHD} ${output_mp4})
        echo ${ffmpeg_cmd} | bash , tình yêu như ngọn nến

        render -y -i input.mp4 -vf subtitles="f=/mnt/775AD44933621551/Project/MMO/youtube/test.ass:force_style='FontName=UTM Bustamalaka,FontSi
        ze=10,OutlineColour=&H66000000,BorderStyle=3'":original_size=1920x1080 002.mp4
        :param timelength:
        :param input_sub:
        :param input_video:
        :param output_vid:
        :return:
        """

        FfmpegCli.check_file_exist(input_sub)
        FfmpegCli.check_file_exist(input_video)
        input = ffmpeg.input(input_video)
        subvid_stream = input['v'].filter('subtitles', input_sub)
        return (
            ffmpeg
                .output(subvid_stream, input['a'],
                        output_vid, acodec='copy', t=timelength)
                .global_args('-shortest')
                .global_args('-threads', '{}'.format(cpucount))
                .global_args("-preset", "ultrafast")
                .run(cmd=ffmpegpath, overwrite_output=True)
        )

    def add_affect_to_video(self, affect_vid: str, video: str, output: str, opacity_val: int):
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
        :param affect_vid:
        :param video:
        :return:
        """
        has_alpha = self.check_alpha_channel(affect_vid)
        if has_alpha:
            FfmpegCli.check_file_exist(affect_vid)
            FfmpegCli.check_file_exist(video)
            bgvideo_stream = ffmpeg.input(video)
            effect_stream = ffmpeg.input(affect_vid)
            streams_list = [bgvideo_stream, effect_stream]
            (
                ffmpeg.filter(streams_list, 'overlay')
                    .output(output, framerate=25)
                    .global_args('-shortest')
                    .global_args('-threads', '{}'.format(cpucount))
                    .global_args("-preset", "ultrafast")
                    .run(cmd=ffmpegpath, overwrite_output=True)
            )
            # self._ffmpeg_input(video)
            # self._ffmpeg_input(affect_vid)
            # self._ffmpeg_input_filter_complex_prefix()
            # self._ffmpeg_input_fill_cmd('overlay ')
            # self._ffmpeg_input_fill_cmd('-shortest')
            # self.ffmpeg_cli_run(self.ffmpeg_cli, output)
        else:
            self.add_nontransparent_effect_to_video(video, affect_vid, output, opacity_val)
        pass

    def add_nontransparent_effect_to_video(self, effect_vid: str, video: str, output: str, opacity_val: int):
        FfmpegCli.check_file_exist(effect_vid)
        FfmpegCli.check_file_exist(video)

        bg_video_alpha = self.check_alpha_channel(video)
        effect_video_alpha = self.check_alpha_channel(effect_vid)

        video_stream = ffmpeg.input(video)['v'].filter('format', 'argb')
        effect_stream = ffmpeg.input(effect_vid)['v'].filter('format', 'argb')

        # format_video_stream = video_stream.filter('format', 'argb')
        # format_effect_strean = effect_stream.filter('format', 'argb')
        opacity = opacity_val / 100
        (
            ffmpeg.filter([effect_stream, video_stream],
                          'blend', all_mode='overlay',
                          all_opacity="{}".format(opacity))
                .output(output)
                .global_args('-shortest')
                .global_args('-threads', '{}'.format(cpucount))
                .global_args("-preset", "ultrafast")
                .run(cmd=ffmpegpath, overwrite_output=True)
        )
        # if bg_video_alpha:
        #     pass
        # if effect_video_alpha:
        #     pass

        # self._ffmpeg_input_filter_complex_prefix()
        # opacity = float(opacity_val / 100)
        # filter_args = "[1:0]format=rgba[a]; \
        #                [0:0]format=rgba[b]; \
        #                [a][b]blend=all_mode='overlay':all_opacity={}".format(opacity)
        # self._ffmpeg_input_fill_cmd(filter_args)
        # self._ffmpeg_input_fill_cmd('-shortest')
        # self.ffmpeg_cli_run(self.ffmpeg_cli, output)
        pass

    def clean_up_mp3_meta_data(self, mp3file, mp3out):
        """
       ffmpeg -i tagged.mp3 -map 0:a -codec:a copy -map_metadata -1 out.mp3
        :param mp3file:
        :return:
        """

        (
            ffmpeg.input(mp3file)['a']
                .output(mp3out, acodec='copy', map_metadata=-1)
                .global_args('-threads', '{}'.format(cpucount))
                .run(cmd=ffmpegpath, overwrite_output=True)
        )
        # FfmpegCli.check_file_exist(mp3file)
        # self._ffmpeg_input(mp3file)
        # self._ffmpeg_input_fill_cmd('-map')
        # self._ffmpeg_input_fill_cmd('0:a')
        # self._ffmpeg_input_fill_cmd('-codec:a')
        # self._ffmpeg_input_fill_cmd('copy')
        # self._ffmpeg_input_fill_cmd('-map_metadata')
        # self._ffmpeg_input_fill_cmd('-1')
        # self.ffmpeg_cli_run(self.ffmpeg_cli, mp3out)
        pass

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
        from backend.utility.TempFileMnger import Mp3TempFile
        tempaudiofile = Mp3TempFile().getfullpath()
        self.clean_up_mp3_meta_data(input_audio, tempaudiofile)
        (
            ffmpeg.output(ffmpeg.input(input_vid)['v'],
                          ffmpeg.input(input_audio)['a']
                          , output_vid, acodec='copy', vcodec='copy')
                .global_args('-shortest')
                .global_args('-threads', '{}'.format(cpucount))
                .global_args("-preset", "ultrafast")
                .run(cmd=ffmpegpath, overwrite_output=True)
        )

        # ffmpeg_cmd = ["ffmpeg", "-y",
        #               "-i", "{}".format(input_vid),
        #               "-i", "{}".format(tempaudiofile),
        #               "-map", "0:v", "-map", "1:a", "-map", "0:v", "-shortest"]
        # self._ffmpeg_input_fill_cmd('-t')
        # self._ffmpeg_input_fill_cmd("{}".format(timeleng))

        # self._ffmpeg_input_fill_cmd('-c')
        # self._ffmpeg_input_fill_cmd('copy')
        # self.ffmpeg_cli_run(ffmpeg_cmd, output_vid, superfast=1)

    def add_logo_to_bg_img(self, input_bg: str,
                           input_logo: str,
                           output: str,
                           coordinate):
        """
        render -i small.mp4 -i avatar.png -filter_complex
                    "[1:v]format=argb,colorchannelmixer=aa=0.5[zork];
                    [0:v][zork]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2"
                    -codec:a copy output.mp4

        :param output:
        :param input_bg:
        :param input_logo:
        :param coordinate:
        :return:
        """

        from render.type import Position
        coordinate: Position
        FfmpegCli.check_file_exist(input_bg)
        FfmpegCli.check_file_exist(input_logo)
        streams_list = [ffmpeg.input(input_bg), ffmpeg.input(input_logo)]

        (
            ffmpeg.filter(streams_list, 'overlay', coordinate.x, coordinate.y)
                .output(output)
                .global_args('-shortest')
                .global_args("-preset", "ultrafast")
                .run(cmd=ffmpegpath, overwrite_output=True)
        )
        # self._ffmpeg_input(input_bg)
        # self._ffmpeg_input(input_logo)
        # self._ffmpeg_input_filter_complex_prefix()
        # filter = "[0:v][1:v]overlay={}:{}" \
        #     .format(coordinate.x, coordinate.y)
        # self._ffmpeg_input_fill_cmd(filter)
        # logger.debug('{}'.format(self.ffmpeg_cli))
        # self.run(self.ffmpeg_cli, output)
        # self.reset_ffmpeg_cmd()

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

    def check_alpha_channel(self, affect_vid):
        data = ffmpeg.probe(affect_vid, cmd=ffprobepath)
        streams = data['streams']
        if len(streams):
            pix_format = streams[0]['pix_fmt']
            if pix_format == 'argb' or pix_format == 'rgba':
                return True
        else:
            return False
        return False
        pass
