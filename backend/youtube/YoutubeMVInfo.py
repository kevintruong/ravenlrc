import json5
import os

from backend.crawler.nct import SongInfo
from backend.utility.Utility import create_mv_config_file, FileInfo, create_hashtag, todict

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


class YoutubeMVInfo:
    def __init__(self, channelname: str, mv_info: str):
        self.channel = channelname
        self.mv_info = mv_info
        self.songinfo = self.get_songinfo(mv_info)
        self.channelinfo = ChannelInfoManger(channelname)
        self.title = '{}\n'.format(self.channelinfo.header.channel + ' || '
                                   + self.songinfo.singerTitle + ' || '
                                   + self.songinfo.title)
        self.hashtags = '{},{}\n'.format(','.join(self.create_hashtags()), ','.join(self.channelinfo.footer.hashtags))

        self.description = self.description_formatter()

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

    def create_hashtags(self):
        singer = create_hashtag(self.songinfo.singerTitle)
        song = create_hashtag(self.songinfo.title)
        return [singer, song]

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
        description = ""
        description = description + self.title
        description = description + (
            '-------------------------------------------------------------------------------------\n')
        description = description + ('{}\n'.format(self.channelinfo.header.channel_info))
        description = description + (
            '-------------------------------------------------------------------------------------\n')
        description = description + ('{}\n'.format(self.channelinfo.header.warning))
        description = description + (
            '-------------------------------------------------------------------------------------\n')
        if self.songinfo.lyric_text:
            description = description + self.songinfo.lyric_text
        description = description + (
            '-------------------------------------------------------------------------------------\n')
        description = description + ('{}\n'.format(self.channelinfo.footer.copyright))
        description = description + self.hashtags
        return description
        pass

    def create_snippet_obj(self):
        pass

    pass


class YtMvConfigSnippet:
    @classmethod
    def tags_formatter(cls, tags: str):
        tags_nospaces = "".join(tags.split())
        tags_list = tags_nospaces.split(',')
        return tags_list

    @classmethod
    def verify_categoryid(cls, id):
        cats = ['', 'Film & Animation', 'Autos & Vehicles', '', '', '', '', '', '', '', 'Music', '', '', '', '',
                'Pets & Animals', '', 'Sports', 'Short Movies', 'Travel & Events', 'Gaming', 'Videoblogging',
                'People & Blogs', 'Comedy', 'Entertainment', 'News & Politics', 'Howto & Style', 'Education',
                'Science & Technology', 'Nonprofits & Activism', 'Movies', 'Anime/Animation', 'Action/Adventure',
                'Classics', 'Comedy', 'Documentary', 'Drama', 'Family', 'Foreign', 'Horror', 'Sci-Fi/Fantasy',
                'Thriller', 'Shorts', 'Shows', 'Trailers']
        this_categoryid = cats[id]
        if len(this_categoryid) == 0:
            return 10  # entertainment categoryId
        return id

    @classmethod
    def create_snippet_from_info(cls, info: YoutubeMVInfo):
        return YtMvConfigSnippet(info.title, info.description, info.hashtags)
        pass

    def __init__(self,
                 title: str,
                 description,
                 tags: str,
                 categoryid=10
                 ):
        self.title = title.replace('\n', '')
        self.description = description
        self.categoryId = self.verify_categoryid(categoryid)
        self.tags = self.tags_formatter(tags)

    def snippet_formatter(self, channel, songinfo: SongInfo):
        pass

    def to_dict(self):
        return todict(self)

    pass


def create_status_obj(self, delaydays):
    from backend.youtube.youtube_uploader import YtMvConfigStatus
    self.status = YtMvConfigStatus(delaydays)
    pass


import unittest


class TestMvDescription(unittest.TestCase):
    def setUp(self):
        self.mvDes = YoutubeMVInfo('timshel', 'Em À')

    def test_get_songinfo(self):
        songinfo = self.mvDes.get_songinfo('Em À')
        print(songinfo)

    def test_get_channel_info(self):
        print(self.mvDes.toJSON())
        self.mvDes.description_formatter()

    def test_create_nhammatthaymuahe(self):
        self.nhammat = YoutubeMVInfo('timshel', 'Nhắm mắt thấy mùa hè')
        description = self.nhammat.description_formatter()
        print(description)

    def test_create_ema(self):
        self.nhammat = YoutubeMVInfo('timshel', 'Em à')
        description = self.nhammat.description_formatter()
        print(description)

    def test_create_huyenthoai(self):
        self.nhammat = YoutubeMVInfo('timshel', 'huyen thoai')
        description = self.nhammat.description_formatter()
        print(description)
