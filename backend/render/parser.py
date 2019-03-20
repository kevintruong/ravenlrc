from backend.crawler.nct import *
from backend.render.type import *
from backend.render.type import Background
from backend.utility.Utility import *
from backend.yclogger import telelog


class Cmder:
    def __init__(self):
        # self.effect: BgEffect = None
        self.background: Background = None

    @abc.abstractmethod
    def run(self):
        pass


class CrawlCmder(Cmder):
    def __init__(self, crawlcmd: dict):
        super().__init__()
        for key in crawlcmd.keys():
            if 'url' == key:
                self.url = crawlcmd[key]
            if 'output' == key:
                self.output = crawlcmd['output']
            else:
                self.output = ContentDir.SONG_DIR.value
        print(self.url + self.output)

    def crawl_parser(self):
        if 'nhaccuatui' in self.url:
            return NctCrawler(self.url)

    def run(self):
        crawler: Crawler = self.crawl_parser()
        return crawler.getdownload(self.output)
        pass


class SongApi:
    def __init__(self, jsondata: dict):
        super().__init__()
        self.watermask = None
        self.song = None
        self.song_url = None
        self.rendertype = RenderType()
        for keyvalue in jsondata.keys():
            if keyvalue == 'song_url':
                self.song_url = jsondata[keyvalue]
            if keyvalue == 'song':
                self.song = SongInfo(jsondata[keyvalue])
            if keyvalue == 'backgrounds':
                self.backgrounds = self.get_list_background(jsondata[keyvalue])
            if keyvalue == 'spectrum':
                self.spectrum = Spectrum(jsondata[keyvalue])
            if keyvalue == 'title':
                self.title = Title(jsondata[keyvalue])
            if keyvalue == 'watermask':
                self.watermask = WaterMask(jsondata[keyvalue])
            if keyvalue == 'lyric':
                self.lyric = Lyric(jsondata[keyvalue])
            if keyvalue == 'rendertype':
                self.rendertype = RenderType(jsondata[keyvalue])
            if keyvalue == 'song_effect':
                self.song_effect = PyJSON(jsondata[keyvalue])
        self.get_song_info_from_url()

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_song_info_from_url(self):
        if self.song is None and self.song_url:
            crawlerdict = {'url': self.song_url}
            crawler = CrawlCmder(crawlerdict)
            self.song: SongInfo = SongInfo(json.loads(crawler.run()))
            pass

    def get_list_background(self, info: list):
        backgrounds = []
        for background_info in info:
            background = Background(background_info)
            backgrounds.append(background)
        return backgrounds
