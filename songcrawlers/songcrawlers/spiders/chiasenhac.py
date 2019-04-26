import re

import scrapy
from songcrawlers.items import SongcrawlersItem


class ChiaSeNhacSpider(scrapy.Spider):
    name = "chiasenhac"
    start_urls = ['https://chiasenhac.vn/bai-hat-moi.html']
    cookies = {
        'csn_listen': 'a%3A1%3A%7Bi%3A1274031%3Ba%3A5%3A%7Bs%3A1%3A%22t%22%3Bs%3A9%3A%22Ph%C3%B4i+Pha%22%3Bs%3A2%3A%22ci%22%3Bs%3A1%3A%223%22%3Bs%3A2%3A%22cl%22%3Bs%3A1%3A%221%22%3Bs%3A3%3A%22url%22%3Bs%3A21%3A%22phoi-pha%7Enguyen-khang%22%3Bs%3A1%3A%22a%22%3Bs%3A13%3A%22Nguy%C3%AAn+Khang%22%3B%7D%7D',
        '_ga': 'GA1.2.1435433785.1555779279',
        '_gid': 'GA1.2.1774725009.1555779279',
        'ads_time': 'i%3A9%3B',
        'PHPSESSID': 'umu4324e1j3m0g6k1o1nshcguq',
        'music_history': 'a%3A1%3A%7Bi%3A0%3Bi%3A2006048%3B%7D',
        'apluuid': 'eccf3f5dbca649279e4b25aa154d028b',
        'label_quality': 'Lossless',
        'csn_popup_pc': 'i%3A1%3B',
        '_gat_gtag_UA_27050676_16': '1',
        '_gat_gtag_UA_27050676_1': '1',
        'csn_popup_beta2': 'i%3A1%3B',
        'XSRF-TOKEN': 'eyJpdiI6IlN4VmVLZkRBMXFtMXpGam9aS2YrbHc9PSIsInZhbHVlIjoid0FTWmlBc3F4dDFBUDZpb3pSdmZRREs1V0t3RlwvcitLTjBhbXV4cmJHZ1MxV0l4R05BNGtibncyMktSZjVNT3UiLCJtYWMiOiIyYjg0YzhkYmM2YTRhZTU1MDFlMjMyZmZiMmU5ZTQwZGM2ZGQwNmUzYmI5ZDM4ZDk0NjRmMDAxNzg2NzAzYzM3In0%3D',
        'chia_se_nhac_session': 'eyJpdiI6IlBJdjBrNHY1eGprNTRNVFpHV0NEMFE9PSIsInZhbHVlIjoiUElmNVJwWlNUYlwvMWEwd2ROamdQaStQdzRZdG14Q0luXC85bFpTQklRVTh4czlFTWJESVZFMUdLM0ZKZ1BHT1VJIiwibWFjIjoiZTgzMDUwNTU2ODc5YWI2NTU5ZjcyMjE4YzE3OTJjMmQzNmE2YTBlNGJmNWViYWRjNTNiMGI1NjFhYWVmYWE3YSJ9',
    }

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.links = []

    def parse(self, response):
        hxs = scrapy.Selector(response)
        all_pages = hxs.xpath("//*[contains(@class, 'pagination')]/li/a/text()").extract()
        numpages = int(str(all_pages[-1]))
        count = 1
        while count < numpages:
            url = "{}?page={}".format(self.start_urls[0], count)
            print(url)
            count = count + 1
            yield response.follow(url, self.parse_song_page)
            break

    def parse_song_page(self, response):
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath("//*[contains(@class, 'media-title mt-0 mb-0')]/a/@href").extract()
        count = 0
        for href in all_links:
            if "chiasenhac.vn/mp3" in href:
                count += 1
                print(href)
                yield scrapy.Request(href, callback=self.parse_song, cookies=self.cookies, headers=self.headers)
                break

    def parse_song(self, response):
        hxs = scrapy.Selector(response)
        songfiles = hxs.xpath("//input[contains(@value, 'data.chiasenhac.com')]/@value").extract()
        title = hxs.xpath("*//div[contains(@class,'title p-3 relative')]/div/h6/text()").extract_first()
        singer = hxs.xpath("*//div[contains(@class,'title p-3 relative')]/div/p/a/text()").extract_first()
        lyric = hxs.xpath(
            "*//div[contains(@id,'lyrics') and contains(@class,'rabbit-lyrics')]/text()").extract()
        lyric = "".join(lyric).replace("  ", "").replace("\n\n", "\n")
        lyrictext = hxs.xpath("*//div[contains(@class,'text-song text-gray p-3')]/text()").extract()
        lyrictext = "".join(lyric).replace("  ", "").replace("\n\n", "\n")
        id = re.search('~(.*).html', response.url).group(1).split('~')[1]
        yield SongcrawlersItem(id=id, singer=singer, title=title, songfiles=songfiles, lyrictext=lyrictext, lyric=lyric,
                               info=response.url)


class SongChiaSeNhacSpider(scrapy.Spider):
    name = 'songcsn'
    start_urls = [
        'https://vn.chiasenhac.vn/mp3/vietnam/v-pop/noi-minh-dung-chan~my-tam~tsvrcb5qqavqhe.html']

    def start_requests(self):
        cookies = {
            'csn_listen': 'a%3A1%3A%7Bi%3A1274031%3Ba%3A5%3A%7Bs%3A1%3A%22t%22%3Bs%3A9%3A%22Ph%C3%B4i+Pha%22%3Bs%3A2%3A%22ci%22%3Bs%3A1%3A%223%22%3Bs%3A2%3A%22cl%22%3Bs%3A1%3A%221%22%3Bs%3A3%3A%22url%22%3Bs%3A21%3A%22phoi-pha%7Enguyen-khang%22%3Bs%3A1%3A%22a%22%3Bs%3A13%3A%22Nguy%C3%AAn+Khang%22%3B%7D%7D',
            '_ga': 'GA1.2.1435433785.1555779279',
            '_gid': 'GA1.2.1774725009.1555779279',
            'ads_time': 'i%3A9%3B',
            'PHPSESSID': 'umu4324e1j3m0g6k1o1nshcguq',
            'music_history': 'a%3A1%3A%7Bi%3A0%3Bi%3A2006048%3B%7D',
            'apluuid': 'eccf3f5dbca649279e4b25aa154d028b',
            'label_quality': 'Lossless',
            'csn_popup_pc': 'i%3A1%3B',
            '_gat_gtag_UA_27050676_16': '1',
            '_gat_gtag_UA_27050676_1': '1',
            'csn_popup_beta2': 'i%3A1%3B',
            'XSRF-TOKEN': 'eyJpdiI6IlN4VmVLZkRBMXFtMXpGam9aS2YrbHc9PSIsInZhbHVlIjoid0FTWmlBc3F4dDFBUDZpb3pSdmZRREs1V0t3RlwvcitLTjBhbXV4cmJHZ1MxV0l4R05BNGtibncyMktSZjVNT3UiLCJtYWMiOiIyYjg0YzhkYmM2YTRhZTU1MDFlMjMyZmZiMmU5ZTQwZGM2ZGQwNmUzYmI5ZDM4ZDk0NjRmMDAxNzg2NzAzYzM3In0%3D',
            'chia_se_nhac_session': 'eyJpdiI6IlBJdjBrNHY1eGprNTRNVFpHV0NEMFE9PSIsInZhbHVlIjoiUElmNVJwWlNUYlwvMWEwd2ROamdQaStQdzRZdG14Q0luXC85bFpTQklRVTh4czlFTWJESVZFMUdLM0ZKZ1BHT1VJIiwibWFjIjoiZTgzMDUwNTU2ODc5YWI2NTU5ZjcyMjE4YzE3OTJjMmQzNmE2YTBlNGJmNWViYWRjNTNiMGI1NjFhYWVmYWE3YSJ9',
        }

        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        # Only chrome, firefox, opera, safari and internet explorer are supported
        # More browsers could be found at:
        # https://developers.whatismybrowser.com/useragents/explore/software_name/
        common_browsers_links = [
            'https://vn.chiasenhac.vn/mp3/vietnam/v-pop/noi-minh-dung-chan~my-tam~tsvrcb5qqavqhe.html']
        for link in common_browsers_links:
            yield scrapy.http.Request(link, cookies=cookies, headers=headers)

    def parse(self, response):
        scrapy.http.Request(self.start_urls[0])
        hxs = scrapy.Selector(response)
        songfiles = hxs.xpath("//input[contains(@value, 'data.chiasenhac.com')]/@value").extract()
        title = hxs.xpath("*//div[contains(@class,'title p-3 relative')]/div/h6/text()").extract_first()
        singer = hxs.xpath("*//div[contains(@class,'title p-3 relative')]/div/p/a/text()").extract_first()
        lyric = hxs.xpath("*//div[contains(@id,'lyrics') and contains(@class,'rabbit-lyrics')]/text()").extract()
        lyric = "".join(lyric).replace("  ", "").replace("\n\n", "\n")
        lyrictext = hxs.xpath("*//div[contains(@class,'text-song text-gray p-3')]/text()").extract()
        lyrictext = "".join(lyric).replace("  ", "").replace("\n\n", "\n")
        id = re.search('~(.*).html', response.url).group(1).split('~')[1]
        yield SongcrawlersItem(id=id, singer=singer, title=title, songfiles=songfiles, lyrictext=lyrictext, lyric=lyric,
                               info=response.url)
