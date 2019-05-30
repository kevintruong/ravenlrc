import psycopg2
from psycopg2 import sql

from backend.db.ravdb import RavDataBase
from backend.utility.Utility import get_hash_from_string


class FilmReq:
    def __init__(self, idreq=None, filmreq=None):
        if filmreq is None:
            raise ValueError("filmreq can not be NONE")
        self.filmreq = filmreq
        if idreq is None:
            self.id = get_hash_from_string(filmreq)


class FilmReqInfoDb(RavDataBase):
    tb_name = 'film_req_tb'

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
                        '                    req text\n'
                        '                );\n'
                        '                '.format(self.tb_name))
            cur.close()
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if self.conn is not None:
                self.conn.close()

    def insert_film_req(self, pageinfo: FilmReq):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql.SQL("INSERT INTO {}  VALUES ( %s,%s) \
                                    ON CONFLICT(id) \
                                    DO NOTHING").format(sql.Identifier(self.tb_name)),
                           [pageinfo.id,
                            pageinfo.filmreq])
            cursor.close()
            self.conn.commit()
        except Exception as exp:
            from backend.yclogger import stacklogger, slacklog
            print(stacklogger.format(exp))
            slacklog.error(stacklogger.format(exp))
        finally:
            self.close()
        pass

    def get_page_info_by_name(self, idreq):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {} WHERE id='{}'".format(self.tb_name, idreq))
            iteminfo = cursor.fetchone()
            if iteminfo:
                return FilmReq(iteminfo[0], iteminfo[1])
            return None
        finally:
            self.close()
        pass

    def list_all(self):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM {}".format(self.tb_name))
            iteminfo = cursor.fetchall()
            if iteminfo:
                pagesinfo = []
                for each_page in iteminfo:
                    pageifo = FilmReq(each_page[0], each_page[1])
                    pagesinfo.append(pageifo)
                return pagesinfo
            return None
        finally:
            self.close()
