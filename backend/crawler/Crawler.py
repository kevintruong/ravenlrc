from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Crawler:
    def __init__(self):
        pass


class SeleniumCrawler(Crawler):
    def __init__(self, url: str):
        super().__init__()
        mobile_emulation = {

            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},

            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}

        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get(url)

    def get_value_element_value(self, callback):
        val = callback(self.driver.page_source)
        return val

    def get_page_source(self):
        return self.driver.page_source

    def reload_page(self, url):
        self.driver.get(url)
