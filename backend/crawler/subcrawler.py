import re
import urllib
from enum import IntEnum
from time import sleep

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options

from backend.subeffect.asseditor import *
from backend.crawler.rc4_py3 import decrypt
import logging

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


class AudioQuanlity(IntEnum):
    AUDIO_UNKNOW = 0
    AUDIO_QUANLITY_128 = 1
    AUDIO_QUANLITY_192 = 0x02
    AUDIO_QUANLITY_320 = 0x04
    AUDIO_QUANLITY_LOSSLESS = 0x08


def download_mp3_file(url: str, quanlity: AudioQuanlity, outputdir=ChromeDownloadDir):
    """
    download an mp3 file using selenium
    :param quanlity:
    :param outputdir:
    :param url:
    :return:
    """
    global losslessdownload, mediumdownload, lowdownload
    audioQuan = AudioQuanlity.AUDIO_UNKNOW
    logger.debug("start")
    options = Options()
    # options.add_argument("--headless")
    options.add_argument('user-data-dir={}'.format(ChromeDataDir))
    logger.debug("Chrome data dir {}".format(ChromeDataDir))
    prefs = {'download.default_directory': '{}'.format(outputdir)}
    # options.add_experimental_option('prefs', prefs)
    # options.set_headless(True)
    fp = webdriver.FirefoxProfile(r'C:\Users\84935\AppData\Local\Temp\rust_mozprofile.rHEUxruhVTGb')
    browser = webdriver.Firefox(fp, options=options, executable_path=r'D:\chromedriver\geckodriver.exe')
    logger.debug("Open url ")
    browser.get(url)
    browser.find_element_by_css_selector("#btnDownloadBox").click()
    import time
    time.sleep(2)
    try:
        downloadbuttons = browser.find_elements_by_css_selector("#divDownloadBox > ul > li")
        # element = browser.find_element_by_css_selector("#divDownloadBox > ul > li:nth-child(3) > a")
    except NoSuchElementException:
        logger.debug("not found loss less")
        return None
    for each in downloadbuttons:
        logger.debug("check {}".format(each.text))
        if each.text == 'Tải Nhạc 128 Kbps':
            logger.debug("found 'Tải Nhạc 128 Kbps'")
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_128
            lowdownload = each
        elif each.text == 'Tải Nhạc 320 Kbps':
            logger.debug("Found 'Tải Nhạc 320 Kbps''")
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_320
            mediumdownload = each
        elif each.text == 'Tải Nhạc Lossless':
            logger.debug("Found 'Tải Nhạc Lossless'")
            losslessdownload = each
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_LOSSLESS
            break
        else:
            logger.debug("not support yet: {}".format(each.text))
    if audioQuan & AudioQuanlity.AUDIO_QUANLITY_LOSSLESS == quanlity:
        logger.debug("AudioQuanlity.AUDIO_QUANLITY_LOSSLESS")
        losslessdownload.click()
    elif audioQuan & AudioQuanlity.AUDIO_QUANLITY_320 == quanlity:
        logger.debug("AudioQuanlity.AUDIO_QUANLITY_320")
        mediumdownload.click()
    elif audioQuan & AudioQuanlity.AUDIO_QUANLITY_128 == quanlity:
        logger.debug("AudioQuanlity.AUDIO_QUANLITY_128")
        lowdownload.click()
    else:
        logger.debug("not support yest ")
        return None
    fileDonwload = wait_for_download(outputdir, 120)
    try:
        if browser.get_window_position():
            logger.debug("check to close browser")
            browser.close()
        return fileDonwload
    except Exception as e:
        logger.debug("Web browser is closed")
        return fileDonwload

# if __name__ == '__main__':
# download_mp3_file(
#     "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html");
# get_sub_from_url(
#     "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")
