import re
import urllib

import requests
# from subcrawler.rc4_py3 import decrypt
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

key = "Lyr1cjust4nct"


def download_lyric(url):
    respoonse = urllib.request.urlopen(url)
    txt: bytes = respoonse.read()
    return txt.decode("utf-8")


def get_sub_from_url(url: str) -> object:
    response = requests.get(url)
    # print("{}".format(response.headers))
    html_body = response._content.decode("utf-8")
    matched_lines = [line for line in html_body.split('\n') if "player.peConfig.xmlURL" in line]
    if matched_lines:
        lyric_conf = re.findall(r'"(.*?)"', matched_lines[0])
        if lyric_conf is not None:
            lyric = requests.get(lyric_conf[0])
            lyric_content = lyric._content.decode("utf-8")
            matched_lines = [line for line in lyric_content.split('\n') if "lyric" in line]
            if matched_lines:
                test = matched_lines[0]
                newtest = test[test.find("[") + 1: test.find("]")]
                lyricurl = newtest[newtest.find("[") + 1:]
                file = download_lyric(lyricurl)
                returndata = decrypt(key, file)
                return returndata
    return None


def download_mp3_file(url: str) -> str:
    """
    download an mp3 file using selenium
    :param url:
    :return:
    """
    options = Options()
    # options.add_argument("--headless")
    browser = webdriver.Chrome()
    browser.get(url)
    browser.find_element_by_class_name("icon_download").click()
    browser.find_element_by_id("downloadBasic")
    download = browser.find_element_by_class_name(name="popup-info-v3-user")
    download_btn = download.find_element_by_id("downloadBasic").click()
    print("{}".format(download_btn))

    pass


if __name__ == '__main__':
    download_mp3_file(
        "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html");
