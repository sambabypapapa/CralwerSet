"""
爬取淘宝有好货推荐商品及所属类型
"""
import time
import datetime
import json
import requests
import random
import CralwerSet.connect_mysql as connect_mysql
import re
from urllib import parse
import easygui as g
import hashlib
from requests.packages import urllib3
import traceback
import pickle
import pymysql

urllib3.disable_warnings()


class youHH():
    def __init__(self):
        self.conn_T = connect_mysql.test()
        self.cur_T = self.conn_T.cursor()

        self.conn_W = connect_mysql.w_shark_erp()
        self.cur_W = self.conn_W.cursor()
        # 数据库已有的文章id列表
        self.have_list = []
        self.users_num = {}
        self.headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; xiaomi mix Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Safari/537.36 AliApp(TB/9.1.0) TTID/600000@taobao_android_9.1.0 WindVane/8.5.0 900X1600 UT4Aplus/0.2.16",
            "Cookie": "_m_h5_tk=36b5227cd1a1e340e4d56bcc93555f2f_1587526955005; _m_h5_tk_enc=7385708053b9b4519913b71659d347aa;"
        }

    def get_cookies(self, response):
        _m_h5_tk = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk'].value
        _m_h5_tk_enc = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk_enc'].value
        cookies = f'_m_h5_tk={_m_h5_tk};_m_h5_tk_enc={_m_h5_tk_enc};'
        self.headers['Cookie'] = cookies
        return cookies

    def get_sign(self, t, token, page):
        """
        执行js，构造sign参数
        :param data:
        :return:
        """
        if page == 1:
            data = token + "&" + str(
                t) + "&12574478&{\"d\":\"{\\\"tce_sid\\\":\\\"1891397\\\",\\\"tce_vid\\\":\\\"0\\\",\\\"tid\\\":\\\"\\\",\\\"tab\\\":\\\"\\\",\\\"topic\\\":\\\"selected_new_0\\\",\\\"count\\\":\\\"\\\",\\\"env\\\":\\\"online\\\",\\\"pageNo\\\":\\\"1\\\",\\\"psId\\\":\\\"51817\\\",\\\"bizCode\\\":\\\"steins.goodItem\\\",\\\"type\\\":\\\"selected_v2\\\",\\\"page\\\":\\\"1\\\",\\\"pageSize\\\":\\\"20\\\",\\\"tabId\\\":\\\"0\\\",\\\"contentIds\\\":\\\"2500000222552474145%2C2500000213511536931\\\",\\\"viewTopicId\\\":\\\"\\\",\\\"line\\\":\\\"\\\",\\\"home_clickItemId\\\":\\\"590236412947\\\",\\\"src\\\":\\\"phone\\\"}\"}"
        #                                                                                                                                   {"d":"{\"tce_sid\":\"1891397\",\"tce_vid\":\"0\",\"tid\":\"\",\"tab\":\"\",\"topic\":\"selected_new_0\",\"count\":\"\",\"env\":\"online\",\"pageNo\":\"1\",\"psId\":\"51817\",\"bizCode\":\"steins.goodItem\",\"type\":\"selected_v2\",\"page\":\"1\",\"pageSize\":\"20\",\"tabId\":\"0\",\"contentIds\":\"2500000211461002193%2C2500000207797210655\",\"viewTopicId\":\"\",\"line\":\"\",\"home_clickItemId\":\"570216112026\",\"src\":\"phone\"}"}

        else:
            data = token + "&" + str(
                t) + "&12574478&{\"d\":\"{\\\"tce_sid\\\":\\\"1891397\\\",\\\"tce_vid\\\":\\\"0\\\",\\\"tid\\\":\\\"\\\",\\\"tab\\\":\\\"\\\",\\\"topic\\\":\\\"selected_new\\\",\\\"count\\\":\\\"\\\",\\\"env\\\":\\\"online\\\",\\\"pageNo\\\":\\\"1\\\",\\\"psId\\\":\\\"51817\\\",\\\"bizCode\\\":\\\"steins.goodItem\\\",\\\"type\\\":\\\"selected_v2\\\",\\\"page\\\":\\\"%s\\\",\\\"pageSize\\\":\\\"20\\\",\\\"tabId\\\":\\\"0\\\",\\\"clickedIds\\\":\\\"\\\",\\\"src\\\":\\\"phone\\\"}\"}" % (
                       page)
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        return sign, parse.quote(data.split("&")[-1])

    def get_content_sign(self, content_id, token, t):
        data = token + "&" + str(
            t) + "&12574478&{\"contentId\":\"%s\",\"source\":\"youhh_tuji\",\"type\":\"h5\",\"params\":\"\",\"business_spm\":\"\",\"track_params\":\"\"}" % (
                   content_id)
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        return sign, parse.quote(data.split("&")[-1])

    def closeSql_T(self):
        """
        断开T数据库连接
        :return:
        """
        self.cur_T.close()
        self.conn_T.close()

    def closeSql_W(self):
        """
        断开W数据库连接
        :return:
        """
        self.cur_W.close()
        self.conn_W.close()

    def quchong(self, text, long, LIST):
        for each in LIST:
            if each[1] == long and text[0] == each[0][0] and text == each[0]:
                return False
        return True

    def getContent(self, content_id):
        """
        :param content_id:文章编号
        :return: 文章内容
        """
        while True:
            self.headers[
                'Referer'] = f'https://market.m.taobao.com/apps/market/content/index.html?contentId={content_id}&source=youhh_tuji'
            temp = int(time.time() * 1000)
            _m_h5_tk = re.findall('_m_h5_tk=[^;]*', self.headers['Cookie'])[0].split('=')[1]
            token = _m_h5_tk.split('_')[0]
            sign, data = self.get_content_sign(content_id, token, temp)
            url = f"https://h5api.m.taobao.com/h5/mtop.taobao.beehive.detail.contentservicenewv2/1.0/?jsv=2.5.1&appKey=12574478&t={temp}&sign={sign}&api=mtop.taobao.beehive.detail.contentservicenewv2&v=1.0&AntiCreep=true&AntiFlood=true&timeout=5000&type=jsonp&dataType=jsonp&callback=mtopjsonp2&data={data}"
            response = requests.get(url, headers=self.headers, verify=False)
            response_text = response.text[12:-1]
            if "令牌过期" in response_text:
                self.get_cookies(response)
            else:
                break
        info = json.loads(response_text)
        time.sleep(random.randint(0, 10))
        text_list = []
        if "photos" in info['data']['models']['content'].keys():
            for photo in info['data']['models']['content']['photos']:
                if 'desc' in photo.keys():
                    text_list.append([photo['desc'], len(photo['desc'].encode())])
        uniqe_text = []
        while len(text_list):
            text, long = text_list.pop()
            if self.quchong(text, long, text_list):
                uniqe_text.append([text, long])
                print(text, long)

        return uniqe_text

    def requestUrl(self, page):
        """
        请求页面
        :param page:
        :return:返回页面json数据
        """
        while True:
            temp = int(time.time() * 1000)
            _m_h5_tk, _m_h5_tk_enc = (re.findall('_m_h5_tk=[^;]*', self.headers['Cookie'])[0].split('=')[1],
                                      re.findall('_m_h5_tk_enc=[^;]*', self.headers['Cookie'])[0].split('=')[1])
            token = _m_h5_tk.split('_')[0]
            sign, data = self.get_sign(temp, token, page)
            url = f'https://h5api.m.taobao.com/h5/mtop.taobao.tceget.steins.gooditem.xget/1.0/?jsv=2.4.5&appKey=12574478&t={temp}&sign={sign}&AntiCreep=true&api=mtop.taobao.tceget.steins.gooditem.xget&v=1.0&dataType=jsonp&timeout=20000&H5Request=true&preventFallback=true&type=jsonp&callback=mtopjsonp2&data={data}'
            response = requests.get(url, headers=self.headers, verify=False)
            response_text = response.text[12:-1]
            if "令牌过期" in response_text:
                self.get_cookies(response)
            else:
                break
        info = json.loads(response_text)
        time.sleep(random.randint(5, 20))
        return info

    def findClass(self, title):
        """
        判断该文章的类型
        :param title:
        :return: 该文章最有可能的类型
        """
        sql = f"""SELECT t6.cat,t5.num FROM (select t4.MAIN_ID MAIN_ID,count(t4.MAIN_ID) num FROM (SELECT  t2.CLASSIFY_ID CLASSIFY_ID FROM (select URL_ID, CONTENT from crawler_commodity_module_description where match(CONTENT) against('{title}') limit 100) t1, cm_commodity t2 where t1.URL_ID=t2.URL_ID ) t3, class_id t4 where t3.CLASSIFY_ID = t4.ID GROUP BY t4.MAIN_ID) t5, class_id t6 WHERE t6.ID=t5.MAIN_ID ORDER BY t5.num desc LIMIT 1;"""
        while True:
            try:
                self.cur_W.execute(sql)
                info = self.cur_W.fetchone()
                break
            except pymysql.err.OperationalError:
                print('由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。')
                self.conn_W.ping(True)
            except pymysql.err.ProgrammingError:
                print(sql)
                return '未知分类'
        if info:
            return info[0][0:-1]
        else:
            return '未知分类'

    def insertEssay(self, contentid, title, mainClass):
        """
        写入数据库
        :param contentid: 文章编号
        :param title: 文章标题
        :param mainClass: 文章最可能的分类
        :return:
        """
        sql = f"""insert into yhh_essays(CONTENT_ID, TITLE, MAIN_CLASSIFY, UPDATE_TIME) values({contentid},'{title.replace("'", '')}','{mainClass}',now()); """
        self.cur_T.execute(sql)

    def insertText(self, text_list, contentId):
        sql = "insert into cm_text_temp(TEXT,`LONG`) values(%s,%s);"
        self.cur_W.executemany(sql, text_list)
        self.cur_T.execute(f"update yhh_essays set GET_CONTENT=1 where ID={contentId};")
        self.conn_T.commit()

    def getHaveList(self):
        """
        获取已存在文章列表
        :return:
        """
        sql = """select CONTENT_ID from yhh_essays;"""
        self.cur_T.execute(sql)
        result = self.cur_T.fetchall()
        if result:
            for each in result:
                self.have_list.append(int(each[0]))
        return self.have_list

    def main(self, id, contentId):
        try:
            text_list = self.getContent(int(str(contentId)[7:]))
            self.insertText(text_list, id)
        except Exception as e:
            traceback.print_exc()
            return False

        return True


def main():
    yhh = youHH()
    # 查询没有文案的记录
    havnt_text_essay_sql = "select ID, CONTENT_ID from yhh_essays where GET_CONTENT=0;"
    yhh.cur_T.execute(havnt_text_essay_sql)
    # 逐条记录查询文案
    for id, content_id in yhh.cur_T.fetchall():
        result = yhh.main(id, content_id)

    yhh.closeSql_T()
    yhh.closeSql_W()


if __name__ == '__main__':
    main()
