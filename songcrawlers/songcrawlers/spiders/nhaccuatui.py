import scrapy
import requests

headers = {
    'authority': 'www.nhaccuatui.com',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'nctads_ck=g49j2tu1f2il4w4w6x64fhof_1554856256954; fbm_414296278689656=base_domain=.nhaccuatui.com; NCT_BALLOON_INDEX=true; __utma=157020004.1165531668.1554856257.1554856257.1555640036.2; __utmc=157020004; __utmz=157020004.1555640036.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); autoPlayNext=true; NCT_AUTH_JWT=eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NTgyMzQyMjMsImxvZ2luTWV0aG9kIjoiMiIsInVzZXJJZCI6IjM1MDA3NTY2IiwibmJmIjoxNTU1NjQyMjIzLCJpYXQiOjE1NTU2NDIyMjMsImRldmljZUlkIjoiMzI2RjQyNjE2RjFFNDUwN0FGOURDQzI0NjUwQzA2MEQifQ.HkrSQiVikuH7-Ap3uziLGILkBm-VvLACQy2bQ6LGMBQ; NCT_BALLOON_INDEX-kevinraven=true; PaymentPageATM=49000; NCT_PAYMENT_DISCOUNT=; NCT_PAYMENT_DISCOUNT_A=; NCT_PAYMENT_AUTORENEW=new; NCT_ONOFF_ADV=1; __utmt=1; NCTNPLP=a32c585f6e8f316dc3d76e6edc2443b538d4ac2314425454f9a6135c898177dc; NCTNPLS=58e5801f60974d1267f8898b44c0af16; NCTCRLS=fb30d00ae64a520529006004e982a291c977687b0ec71b995d9b3d1825eec529cab3d7adcee90884af916eb9193e1849a885b80bafbcae99849cdd6f25e8953d03f50587f73a6f8075f424d7283129c4664d563f2e3c2f19f34f35e0d98e1d84cf83f3eda9c2cd35fd9df68a92e890b0ed4cb2c8721131fa1f94214cc3d24c11f03efe89190478615b3b70a50bb3a32b262d592b918d40527c17a70549b4d3662173ab5acb841066cb2296ad0f92a6c1bc7df478c155dfac51c4a4df8a017f98a6c5d9e220fdd0e44df40b5ea314929853d760c0d412c0dcb0dfbbdb502be6fb8a9f53d395d63df48f091d379d3349eb; 80085=401d10668d97dffa38c487e85e9; JSESSIONID=1s40xulznm0gi1x28vfwijgodk; __utmb=157020004.61.9.1555642662756',
}

response = requests.get(
    'https://www.nhaccuatui.com/bai-hat/i-cant-get-enough-benny-blanco-ft-tainy-ft-selena-gomez-ft-j-balvin.x8NBvTmmMGpE.html',
    headers=headers)


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }


class SongsSpider(scrapy.Spider):
    name = "songcrawl"
    start_urls = ['https://nhaccuatui.com/nghe-si.html']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.links = []

    def parse(self, response):
        hxs = scrapy.Selector(response)
        # extract all links from page
        all_links = hxs.xpath('*//a/@href').extract()
        # follow links to author pages
        self.links.append(response.url)
        for href in all_links:
            if "www.nhaccuatui.com/nghe-si/" in href:
                yield response.follow(href, self.parse_nghe_si_alphabet)

    def parse_nghe_si_alphabet(self, response):
        # ul_listItem > li:nth-child(1)
        print(response.url)
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('//a[contains(@href, "nghe-si-")]/@href').extract()
        print(all_links)
        for each_link in all_links:
            yield response.follow(each_link, self.parse_nghesi)
        all_links = hxs.xpath('//a[contains(@href, "nghe-si") and contains(@class,"number")]/@href').extract()
        print(all_links)
        for each_link in all_links:
            yield response.follow(each_link, self.parse_nghe_si_alphabet_detail)
        pass
    
    def parse_nghe_si_alphabet_detail(self, response):
        # ul_listItem > li:nth-child(1)
        print(response.url)
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('//a[contains(@href, "nghe-si-")]/@href').extract()
        print(all_links)
        for each_link in all_links:
            print(each_link)
            yield response.follow(each_link, self.parse_nghesi)
            pass

    def parse_nghesi(self, response):
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('//a[contains(@href, ".bai-hat.html")]/@href').extract()
        for eachlinks in all_links:
            yield response.follow(eachlinks, self.parse_nghesibaihat)

    def parse_nghesibaihat(self, response):
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('//a[contains(@href, "/bai-hat/")]/@href').extract()
        all_links = list(set(all_links))
        for song in all_links:
            with open('/tmp/song.txt', 'a+') as songfile:
                songfile.writelines(song)
                songfile.write('\n')
        all_links = hxs.xpath('//a[contains(@href, ".bai-hat.") and contains(@class,"number")]/@href').extract()
        all_links = list(set(all_links))
        for each_links in all_links:
            yield response.follow(each_links, self.parse_nghesibaihat_detail)

    def parse_nghesibaihat_detail(self, response):
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('//a[contains(@href, "/bai-hat/")]/@href').extract()
        all_links = list(set(all_links))
        for song in all_links:
            with open('/tmp/song.txt', 'a+') as songfile:
                songfile.write(song)
                songfile.write('\n')
        pass
    # def parse(self, response):
    # 
    #     page = response.url.split("/")[-2]
    #     filename = 'quotes-%s.html' % page
    #     for quote in response.css('div.quote'):
    #         yield {
    #             'text': quote.css('span.text::text').get(),
    #             'author': quote.css('small.author::text').get(),
    #             'tags': quote.css('div.tags a.tag::text').getall(),
    #         }
