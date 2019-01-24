import json5
import os

from backend.crawler.nct import SongInfo
from backend.utility.Utility import create_mv_config_file, FileInfo

cur_dir = os.path.dirname(os.path.realpath(__file__))
build_cmder_dir = os.path.join(cur_dir, '..\content\BuildCmd')
channelinfodir = os.path.join(cur_dir, '..\content\ChannelInfo')


class DescriptionHeader:
    def __init__(self, header: dict):
        if 'channel' in header:
            self.channel = header['channel']
        if 'info' in header:
            self.channel_info = header['info']
        if 'warning' in header:
            self.warning = header['warning']


class DescriptionFooter:
    def __init__(self, footer: dict):
        if 'copyright' in footer:
            self.copyright = footer['copyright']
        if 'hashtags' in footer:
            self.hashtags = footer['hashtags']


class ChannelInfoManger:
    @staticmethod
    def get_channel_info_config(channelname):
        listfiles = os.listdir(channelinfodir)
        for file in listfiles:
            if channelname in file:
                return os.path.join(channelinfodir, file)
        raise FileNotFoundError('Not found {} in {}'.format(channelname, channelinfodir))

    def get_channel_info(self, channelname):
        try:
            infofile = self.get_channel_info_config(channelname)
            with open(infofile, 'r', encoding='utf-8') as finfo:
                channelinfo = json5.load(finfo)
            return channelinfo
        except Exception as exp:
            raise exp

    def __init__(self, channelname: str):
        channelinfo = self.get_channel_info(channelname)
        if 'header' in channelinfo:
            self.header = DescriptionHeader(channelinfo['header'])
        if 'footer' in channelinfo:
            self.footer = DescriptionFooter(channelinfo['footer'])

        pass

    def toJSON(self):
        return json5.dumps(self, default=lambda o: o.__dict__,
                           sort_keys=True, indent=4)


class MvDescription:
    def __init__(self, channelname: str, mv_info: str):
        self.channel = channelname
        self.mv_info = mv_info
        self.songinfo = self.get_songinfo(mv_info)
        self.channelinfo = ChannelInfoManger(channelname)
        pass

    def toJSON(self):
        return json5.dumps(self, default=lambda o: o.__dict__,
                           sort_keys=True, indent=4)

    @staticmethod
    def get_mv_build_config(buildmv):
        buildmv = create_mv_config_file(buildmv)
        fileinfo = FileInfo(buildmv)
        name = fileinfo.name
        listfiles = os.listdir(build_cmder_dir)
        for file in listfiles:
            if name in file:
                return os.path.join(build_cmder_dir, file)
        raise FileNotFoundError('Not found {} in {}'.format(buildmv, build_cmder_dir))

    def get_songinfo(self, buildmv):
        mvconfig_file = self.get_mv_build_config(buildmv)
        with open(mvconfig_file, 'r') as fileconfig:
            mvconfig = json5.load(fileconfig)
            if 'songinfo' in mvconfig:
                return SongInfo(mvconfig['songinfo'])

    def description_formatter(self):
        """
        <Header_channel>
        📷 <Song_Title>
        ✪ Follow <Channel_name>
            • Facebook: <channel_facebook_link>
            • Youtube: <channel_youtube_link>
        -------------------------------------------------------------------------------------
        <lyric text>
        -------------------------------------------------------------------------------------
        <Singer info>
        -------------------------------------------------------------------------------------
        <Footer_channel>
        ●  Nếu có bất cứ thắc mắc, khiếu nại nào về bản quyền hình ảnh cũng như âm nhạc có trong video mong chủ sở hữu \
        liên hệ trực tiếp với tôi qua địa chỉ Email: Muadingangphoofficial@gmail.com. Hoặc liên hệ qua Fanpage. Xin cảm\
        ơn!
        -------------------------------------------------------------------------------------
        © Copyright by <channel_name> ☞ Do not reup!
        ------------------------------------------------------------------------------------
        <[#hashtags]>

        :return:
        """
        with open('description.txt', 'w', encoding='utf-8') as des_file:
            des_file.writelines('{}\n'.format(self.channelinfo.header.channel + '||'
                                              + self.songinfo.singerTitle + '||'
                                              + self.songinfo.title))
            des_file.writelines(
                '-------------------------------------------------------------------------------------\n')
            des_file.writelines('{}\n'.format(self.channelinfo.header.channel_info))
            des_file.writelines(
                '-------------------------------------------------------------------------------------\n')
            des_file.writelines('{}\n'.format(self.channelinfo.header.warning))
            des_file.writelines(
                '-------------------------------------------------------------------------------------\n')

            from backend.subeffect.asseditor import load_lrc_file
            assfile = load_lrc_file(self.songinfo.lyric)
            for line in assfile.events:
                des_file.write(line.text + '\n')

            des_file.writelines(
                '-------------------------------------------------------------------------------------\n')
            des_file.writelines('{}\n'.format(self.channelinfo.footer.copyright))
            des_file.writelines('{}\n'.format(','.join(self.channelinfo.footer.hashtags)))
        pass

    def create_snippet_obj(self, songinfo: SongInfo):
        title = r'[{}][Lyric][{}] {}'.format(self.channel, songinfo.singerTitle, songinfo.title)
        self.description_formatter()
        pass

    def create_status_obj(self, delaydays):
        from backend.youtube.youtube_uploader import YtMvConfigStatus
        self.status = YtMvConfigStatus(delaydays)
        pass


import unittest


class TestMvDescription(unittest.TestCase):
    def setUp(self):
        self.mvDes = MvDescription('timshel', 'Em À')

    def test_get_songinfo(self):
        songinfo = self.mvDes.get_songinfo('Em À')
        print(songinfo)

    def test_get_channel_info(self):
        print(self.mvDes.toJSON())
        self.mvDes.description_formatter()

    def test_create_nhammatthaymuahe(self):
        self.nhammat = MvDescription('timshel', 'Nhắm mắt thấy mùa hè')
        self.nhammat.description_formatter()
