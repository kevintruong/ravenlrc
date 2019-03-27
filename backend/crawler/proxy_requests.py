import random
import time

import requests


class ProxyRequests:
    proxy_source = 'https://proxy.rudnkh.me/txt'

    def __init__(self):
        self.proxylist = None
        self.proxydict = []
        pass

    def get_proxy_req(self):
        self.proxylist = requests.get(self.proxy_source).text.split('\n')
        for each_proxy in self.proxylist:
            self.proxydict.append({'https': each_proxy})

    def get(self, url, **kwargs):
        while True:
            try:
                current_proxydict = random.choice(self.proxydict)
                print(current_proxydict)
                rsp = requests.get(url, proxies=current_proxydict, timeout=5, **kwargs)
                return rsp
            except Exception as exp:
                print(exp)


import unittest


class TestProxyRequest(unittest.TestCase):
    def setUp(self):
        self.url = r'https://c1-sd-vdc.nixcdn.com/NhacCuaTui978/ChiCanAnhNoi-Mei-5904542.mp3?st=Pb7R9HuxJzU3gL-Eug_PxA&e=1553739412'
        self.proxyRequests = ProxyRequests()
        self.proxyRequests.get_proxy_req()

    def test_get_proxylist(self):
        self.proxyRequests.get_proxy_req()
        print(self.proxylist)

    def test_get_url(self):
        while True:
            print("test")
            t = time.process_time()
            # do some stuff
            mp3file = self.proxyRequests.get(url=self.url, allow_redirects=True)
            with open('test.mp3', 'wb') as mp3filefd:
                mp3filefd.write(mp3file.content)
                mp3filefd.close()
            elapsed_time = time.process_time() - t
            print('final test {}'.format(elapsed_time))
            time.sleep(2)
            # print(respondse.text)
