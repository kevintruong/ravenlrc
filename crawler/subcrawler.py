import logging
import re
import urllib
from time import sleep

import requests

from crawler.rc4_py3 import decrypt
from subeffect.asseditor import *

key = "Lyr1cjust4nct"
curDir = os.path.dirname(__file__)

ChromeDataDir = "{}/UserData".format(curDir)
ChromeDownloadDir = "{}/Download".format(curDir)

if not os.path.isdir(ChromeDownloadDir):
    os.mkdir(ChromeDownloadDir)
if not os.path.isdir(ChromeDataDir):
    os.mkdir(ChromeDataDir)

logger = logging.getLogger('kendebug')


def download_lyric(url):
    respoonse = urllib.request.urlopen(url)
    txt: bytes = respoonse.read()
    return txt.decode("utf-8")


def get_sub_from_url(url: str) -> object:
    response = requests.get(url)
    # logger.debug("{}".format(response.headers))
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


def get_sub_file(url: str, dir: str):
    import codecs
    sub_ass = get_sub_from_url(url)
    subfiletmp = os.path.join(dir, "test.lrc")
    with codecs.open(subfiletmp, 'w', "utf-8") as f:
        f.write(sub_ass)
    return subfiletmp


def crawl_lyric(url: str, lyric_outfile: str):
    import codecs
    sub_ass = get_sub_from_url(url)
    with codecs.open(lyric_outfile, 'w', "utf-8") as f:
        f.write(sub_ass)
    return lyric_outfile


def wait_for_start_download(directory, timeout, nfiles=None):
    """
       Wait for downloads to finish with a specified timeout.

       Args
       ----
       directory : str
           The path to the folder where the files will be downloaded.
       timeout : int
           How many seconds to wait until timing out.
       nfiles : int, defaults to None
           If provided, also wait for the expected number of files.

       """
    logger.debug("Wait for download start")
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        sleep(1)
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            extension = os.path.splitext(fname)[1][1:]
            if extension == "crdownload":
                logger.debug("Download start after {}".format(seconds))
                return os.path.join(directory, fname)
        seconds += 1
    return None


def wait_for_download(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    global file
    download_file = wait_for_start_download(directory, 120)
    logger.debug("wait for download copmplete {}".format(download_file))
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        sleep(1)
        dl_wait = False
        if os.path.isfile(download_file):
            logger.debug("wait for {} complete".format(download_file))
            dl_wait = True
        seconds += 1
    logger.debug("Download complete after {}".format(seconds))
    return os.path.join(directory, os.path.splitext(download_file)[0])
    # return download_file


import unittest


class Test_Selenium_crawler(unittest.TestCase):
    def setUp(self):
        self.url = 'https://www.nhaccuatui.com/bai-hat/chi-can-anh-noi-mei.AjyxRsfbKTld.html'
