import json
import os
import subprocess

import psycopg2
import requests
from psycopg2 import sql

from backend.db.ravdb import RavDataBase
from backend.yclogger import slacklog, stacklogger, telelog

CurDir = os.path.dirname(os.path.realpath(__file__))
GetTokenScript = os.path.join(CurDir, 'gettoken.php')


def php(script_path, username, password):
    p = subprocess.Popen(['php', '-f', script_path, username, password], stdout=subprocess.PIPE)
    result = p.communicate()[0]
    return result


class PageInfo:
    def __init__(self, id, name, token, account):
        self.id = id
        self.page_name = name
        self.token = token
        self.account = account

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)


class AccInfo:
    def __init__(self,
                 username,
                 password,
                 token=None):
        self.username = username
        self.password = password
        if token:
            self.token = token
        else:
            self.token = self.gettoken()
        # self.pages = []
        # self.collect_pagesinfo()
        # self.toJSON()

    def gettoken(self):
        get_token = php(GetTokenScript, "{}".format(self.username),
                        "{}".format(self.password)).decode('utf-8')
        userinfo = json.loads(get_token)
        token = userinfo['access_token']
        return token

    def get_accounts_info(self):
        payload = {'method': 'get', 'access_token': self.token}
        fbrsp = requests.get('https://graph.facebook.com/v2.8/me/accounts?limit=1000', payload).json()
        return fbrsp['data']

    def get_pages_info(self):
        pages_info = []
        account_info = self.get_accounts_info()
        for each_page in account_info:
            pageinfo = PageInfo(each_page['id'],
                                each_page['name'],
                                each_page['access_token'], self.username)
            pages_info.append(pageinfo)
        return pages_info

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=2)


class FbPageInfoDb(RavDataBase):
    tb_name = 'fb_pageinfo_tb'

    def __init__(self):
        super().__init__()
        self.create_schema()

    def create_schema(self):
        try:
            self.connect()
            cur = self.conn.cursor()
            cur.execute('\n'
                        '                CREATE TABLE IF NOT EXISTS {}(\n'
                        '                    id text  PRIMARY KEY,\n'
                        '                    page_name text,\n'
                        '                    token text,\n'
                        '                    account text\n'
                        '                );\n'
                        '                '.format(self.tb_name))
            cur.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

    def insert_page_info(self, pageinfo: PageInfo):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql.SQL("INSERT INTO {}  VALUES ( %s,%s,%s,%s) \
                                    ON CONFLICT(id) \
                                    DO NOTHING").format(sql.Identifier(self.tb_name)),
                           [pageinfo.id,
                            pageinfo.page_name,
                            pageinfo.token,
                            pageinfo.account])
            cursor.close()
            self.conn.commit()
        except Exception as exp:
            from backend.yclogger import stacklogger, slacklog
            print(stacklogger.format(exp))
            slacklog.error(stacklogger.format(exp))
        finally:
            self.close()
        pass

    def get_page_info_by_name(self, name):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {} WHERE page_name='{}'".format(self.tb_name, name))
            iteminfo = cursor.fetchone()
            if iteminfo:
                return PageInfo(iteminfo[0], iteminfo[1], iteminfo[2], iteminfo[3])
            return None
        finally:
            self.close()
        pass

    def list_all_page_info(self):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {}".format(self.tb_name))
            iteminfo = cursor.fetchall()
            if iteminfo:
                pagesinfo = []
                for each_page in iteminfo:
                    pageifo =  PageInfo(each_page[0],each_page[1],each_page[2],each_page[3])
                    pagesinfo.append(pageifo)
                return pagesinfo
            return None
        finally:
            self.close()


class FbAccountInfoDb(RavDataBase):
    tb_name = 'fb_acc_info_tb'

    def __init__(self):
        super().__init__()

    def create_schema(self):
        try:
            self.connect()
            cur = self.conn.cursor()
            cur.execute('\n'
                        '                CREATE TABLE IF NOT EXISTS {}(\n'
                        '                    username text  PRIMARY KEY,\n'
                        '                    password text,\n'
                        '                    token text\n'
                        '                );\n'
                        '                '.format(self.tb_name))
            cur.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            raise error
        finally:
            if self.conn is not None:
                self.conn.close()

    def insert_acc_info(self, accinfo: AccInfo):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql.SQL("INSERT INTO {}  VALUES ( %s,%s,%s) \
                                    ON CONFLICT(username) \
                                    DO NOTHING").format(sql.Identifier(self.tb_name)),
                           [accinfo.username,
                            accinfo.password,
                            accinfo.token])
            cursor.close()
            self.conn.commit()
        except Exception as exp:
            from backend.yclogger import stacklogger, slacklog
            print(stacklogger.format(exp))
            slacklog.error(stacklogger.format(exp))
        finally:
            self.close()

    def get_acc_info_by_name(self, name):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {} WHERE username='{}'".format(self.tb_name, name))
            iteminfo = cursor.fetchone()
            if iteminfo:
                return AccInfo(iteminfo[0], iteminfo[1], iteminfo[2])
            return None
        finally:
            self.close()


class FbAccInfoManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def list_all_pages_info(self):
        listpage = FbPageInfoDb().list_all_page_info()
        pagesinfo = []
        for each_page in listpage:
            paginfo = PageInfo(each_page[0], each_page[1], each_page[2], each_page[3])
            pagesinfo.append(paginfo)
        if len(pagesinfo):
            return pagesinfo
        return None

    def get_page_info(self, pagename: str):
        pageinfo = FbPageInfoDb().get_page_info_by_name(pagename)
        return pageinfo

    def update_all_pages_in_acc(self, accinfo: AccInfo):
        try:
            pagesinfo = accinfo.get_pages_info()
            FbAccountInfoDb().insert_acc_info(accinfo)
            for each_page in pagesinfo:
                FbPageInfoDb().insert_page_info(each_page)

        except Exception as exp:
            infoexp = stacklogger.format(exp)
            print(infoexp)
            slacklog.error(infoexp)
            raise exp

    def add_acc_info(self):
        try:
            accinfo = AccInfo(self.username, self.password)
            self.update_all_pages_in_acc(accinfo)
        except Exception as exp:
            infoexp = stacklogger.format(exp)
            print(infoexp)
            slacklog.error(infoexp)


import unittest


class TestFbAccountDb(unittest.TestCase):
    def setUp(self) -> None:
        self.testacc = AccInfo('kevinelg', 'thisistest', 'thisis_mytoken')
        self.testpageinfo = PageInfo('pageid', 'timshel page', 'page token', self.testacc.username)
        self.jsoninfo = '/mnt/Data/Project/ytcreatorservice/publisher/facebook/db/pages.json'
        pass

    def test_insert_acc(self):
        FbAccountInfoDb().insert_acc_info(self.testacc)
        accinfo = FbAccountInfoDb().get_acc_info_by_name('kevinelg')
        self.assertIsNotNone(accinfo)
        print(accinfo.toJSON())
        accinfo = FbAccountInfoDb().get_acc_info_by_name('kevin')
        self.assertIsNone(accinfo)
        FbAccountInfoDb().destroy(FbAccountInfoDb.tb_name)
        accinfo = FbAccountInfoDb().get_acc_info_by_name('kevinelg')
        self.assertIsNone(accinfo)

    def test_insert_find_acc(self):
        FbPageInfoDb().insert_page_info(self.testpageinfo)
        pageinfo = FbPageInfoDb().get_page_info_by_name(self.testpageinfo.page_name)
        print(pageinfo.toJSON())
        FbPageInfoDb().destroy(FbPageInfoDb.tb_name)
        pageinfo = FbPageInfoDb().get_page_info_by_name(self.testpageinfo.page_name)
        self.assertIsNone(pageinfo)

    # def test_import_page_from_json(self):
    #     with open(self.jsoninfo, 'r') as jsoninfo:
    #         data = json.load(jsoninfo)
    #     accinfo = AccInfo(data['username'], data['password'], data['token'])
    #     FbAccountInfoDb().insert_acc_info(accinfo)
    #     pagesinfo = accinfo.get_pages_info()
    #     for each_page in pagesinfo:
    #         FbPageInfoDb().insert_page_info(each_page)


class Test_AccManager(unittest.TestCase):
    def setUp(self) -> None:
        self.accmnger = FbAccInfoManager('kevinelg', 'thienhanh')
        pass

    def test_list_all_pages(self):
        pagesinfo = self.accmnger.list_all_pages_info()
        if pagesinfo:
            for each_page in pagesinfo:
                print("{}".format(each_page.toJSON()))
