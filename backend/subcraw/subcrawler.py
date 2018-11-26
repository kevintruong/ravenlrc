import os
import re
import time
import urllib
from enum import IntEnum

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from backend.subcraw.rc4_py3 import decrypt
from backend.subcraw.asseditor import *

key = "Lyr1cjust4nct"
curDir = os.path.dirname(__file__)

ChromeDataDir = "{}/UserData".format(curDir)
ChromeDownloadDir = "{}/Download".format(curDir)

if not os.path.isdir(ChromeDownloadDir):
    os.mkdir(ChromeDownloadDir)
if not os.path.isdir(ChromeDataDir):
    os.mkdir(ChromeDataDir)


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


def get_sub_file(url: str, dir: str):
    import codecs
    sub_ass = get_sub_from_url(url)
    subfiletmp = os.path.join(dir, "test.lrc")
    with codecs.open(subfiletmp, 'w', "utf-8") as f:
        f.write(sub_ass)
    return subfiletmp


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
    print("Wait for download start")
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            extension = os.path.splitext(fname)[1][1:]
            if extension == "crdownload":
                print("Download start after {}".format(seconds))
                return fname
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
    print("wait for download copmplete")
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            extension = os.path.splitext(fname)[1][1:]
            if extension == "crdownload":
                dl_wait = True
            file = fname

        seconds += 1
    print("Download complete after {}".format(seconds))
    return os.path.join(directory, file)


class AudioQuanlity(IntEnum):
    AUDIO_UNKNOW = 0
    AUDIO_QUANLITY_128 = 1
    AUDIO_QUANLITY_192 = 0x02
    AUDIO_QUANLITY_320 = 0x04
    AUDIO_QUANLITY_LOSSLESS = 0x08


def download_mp3_file(url: str, outputdir: str, quanlity: AudioQuanlity):
    """
    download an mp3 file using selenium
    :param outputdir:
    :param url:
    :return:
    """
    global losslessdownload, mediumdownload, lowdownload
    audioQuan = AudioQuanlity.AUDIO_UNKNOW
    print("start")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('user-data-dir={}'.format(ChromeDataDir))
    prefs = {'download.default_directory': '{}'.format(outputdir)}
    options.add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(chrome_options=options)
    print("Open url ")
    browser.get(url)
    browser.find_element_by_css_selector("#btnDownloadBox").click()
    time.sleep(2)
    try:
        downloadbuttons = browser.find_elements_by_css_selector("#divDownloadBox > ul > li")
        # element = browser.find_element_by_css_selector("#divDownloadBox > ul > li:nth-child(3) > a")
    except NoSuchElementException:
        print("not found loss less")
        return None
    for each in downloadbuttons:
        if each.text == 'Tải Nhạc 128 Kbps':
            print("found 'Tải Nhạc 128 Kbps'")
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_128
            lowdownload = each
        elif each.text == 'Tải Nhạc 320 Kbps':
            print("Found 'Tải Nhạc 320 Kbps''")
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_320
            mediumdownload = each
        elif each.text == 'Tải Nhạc Lossless':
            print("Found 'Tải Nhạc Lossless'")
            losslessdownload = each
            audioQuan |= AudioQuanlity.AUDIO_QUANLITY_LOSSLESS
            break
        else:
            print("not support yet: {}".format(each.text))
    if audioQuan & AudioQuanlity.AUDIO_QUANLITY_LOSSLESS == quanlity:
        losslessdownload.click()
    elif audioQuan & AudioQuanlity.AUDIO_QUANLITY_320 == quanlity:
        mediumdownload.click()
    elif audioQuan & AudioQuanlity.AUDIO_QUANLITY_128 == quanlity:
        lowdownload.click()
    else:
        print("not support yest ")
    fileDonwload = wait_for_download(outputdir, 120)
    browser.close()
    return fileDonwload


if __name__ == '__main__':
    # download_mp3_file(
    #     "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html");
    get_sub_from_url(
        "https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html")
