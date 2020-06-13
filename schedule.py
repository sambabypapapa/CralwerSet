import CralwerSet.connect_mysql as connect_mysql
import requests


class schedule():
    def __init__(self, sql, fun):
        self.conn = None
        self.cur = None
        self.result = None
        self.classes = self.connect_sql(sql, fun)

    def connect_sql(self, sql, fun):
        self.conn = fun
        self.cur = self.conn.cursor()
        self.cur.execute(sql)
        self.result = self.cur.fetchall()
        return list(self.result)

    def pop(self):
        return self.classes.pop()


class ip():
    def __init__(self):
        self.ip_list = []

    def get_ip(self):
        if not self.ip_list:
            url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&pack=68070&ts=0&ys=0&cs=0&lb=3&sb=0&pb=4&mr=1&regions='
            response = requests.get(url).text
            self.ip_list = response.split('\r')[1:]
            # ip = result['data'][0]['ip'] + ':' + str(result['data'][0]['port'])
            # ip = re.findall('(?:(?:[01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}(?:[01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5]):\d{4,5}', response)
            return self.ip_list[0]

    def ip_pop(self):
        self.ip_list = []

