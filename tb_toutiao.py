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


class touTiao():
    def __init__(self):
        self.conn_T = connect_mysql.test()
        self.cur_T = self.conn_T.cursor()
        self.conn_W = connect_mysql.w_shark_erp()
        self.cur_W = self.conn_W.cursor()

        self.CLASS = {
            "新品": "1375",
            "首页": "1203",
            "新鲜": "1518",
            "评测": "1363",
            "园艺": "1379",
            "影视": "1516",
            "游戏": "1370",
            "二次 ": "1359",
            "垂钓": "1362",
            "数码": "1387",
            "优惠": "3626",
            "如何": "1378",
            "居家": "1377",
            "视频": "1340",
            "型男": "1361",
            "汽车": "1341",
            "摄影": "1360",
            "手机": "1513",
            "美妆": "1372",
            "萌宠": "1342",
            "旅行": "1514",
            "精选": "1204",
            "美搭": "1373",
            "运动": "1369",
            "没事": "1358",
            "母婴": "1364",
        }
        self.headers = {
            "Referer": "https://market.m.taobao.com/app/mtb/headline/pages/portal?spm=a215s.7406091.home_m_h_v5_toutiao_corner_1.3&utparam=%7B%22ranger_buckets_native%22%3A%22tsp2584_22605%22%7D&scm=1007.home_headline.headline.d&wh_weex=true&wx_navbar_hidden=true&_wx_statusbar_hidden=hidden_light_text&feedListFeeds=true&columnId=1206&pushFeedIds=209933620800,200253499132",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; xiaomi mix Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Safari/537.36 AliApp(TB/9.1.0) TTID/600000@taobao_android_9.1.0 WindVane/8.5.0 900X1600 UT4Aplus/0.2.16",
            "Cookie": "_m_h5_tk=d2fd278808f43520fbcbdc710af0923c_1589783019427;_m_h5_tk_enc=53dc2d73b37a50c68dbf4bf9acc83c02"
        }
        self.have_list = []
        self.context = ''

    def get_cookies(self, response):
        _m_h5_tk = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk'].value
        _m_h5_tk_enc = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk_enc'].value
        cookies = f'_m_h5_tk={_m_h5_tk};_m_h5_tk_enc={_m_h5_tk_enc};'
        self.headers['Cookie'] = cookies
        return cookies

    def get_sign(self, t, token, entityId):
        """
        执行js，构造sign参数
        :param data:
        :return:
        """
        if not self.context:
            data = token + '&' + str(
                t) + '&12574478&' + '{"entityId":"' + entityId + r'","version":"1.0","userType":1,"action":"1","params":"{\"spm\":\"a215s.7406091.home_m_h_v5_toutiao_corner_1.3\",\"utparam\":\"{\\\"ranger_buckets_native\\\":\\\"tsp2584_22605\\\"}\",\"scm\":\"1007.home_headline.headline.d\",\"wh_weex\":\"true\",\"wx_navbar_hidden\":\"true\",\"_wx_statusbar_hidden\":\"hidden_light_text\",\"feedListFeeds\":\"true\",\"columnId\":\"1206\"}","smart_ui":"{\"ui_layout\":\"toutiao_v3_default\",\"g_size\":\"1\",\"trackInfo\":\"smartui={\\\"ui_type\\\":0,\\\"trackInfo\\\":\\\"/dacu.1.1.6-----scm=1007.18501.117246.0&pvid=pvid&utLogMap=%7B%22x_algo_paras%22%3A%221007.18501.117246.0%3Apvid%3A0%3A%3A0%3A%3A%3Aitem%3Apv%3A___78559%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A0-0-0-0%3A%3A%3A%3A78559-toutiao%23%23v3-toutiao%23%23v3-tce-0-0-0-0%3Ae1e3f2ee-1b15-42b9-bfe1-78cc330e5f25%22%7D-----H46747618\\\",\\\"pvid\\\":\\\"e1e3f2ee-1b15-42b9-bfe1-78cc330e5f25\\\",\\\"ui_id\\\":78559,\\\"scene\\\":\\\"toutiao_v3\\\"}\",\"ui_fields\":\"{}\",\"_pvuuid\":\"e1e3f2ee-1b15-42b9-bfe1-78cc330e5f25\",\"ui_id\":\"78559\"}"}'
        else:
            data = token + '&' + str(
                t) + '&12574478&{"entityId":"' + entityId + r'","version":"1.0","userType":1,"action":"3","params":"{\"spm\":\"a215s.7406091.home_m_h_v5_toutiao_corner_1.3\",\"utparam\":\"{\\\"ranger_buckets_native\\\":\\\"tsp2584_22605\\\"}\",\"scm\":\"1007.home_headline.headline.d\",\"wh_weex\":\"true\",\"wx_navbar_hidden\":\"true\",\"_wx_statusbar_hidden\":\"hidden_light_text\",\"feedListFeeds\":\"true\",\"columnId\":\"1206\",\"context\":\"' + self.context + r'\"}","smart_ui":"{\"ui_layout\":\"toutiao_v3_default\",\"g_size\":\"1\",\"trackInfo\":\"smartui={\\\"ui_type\\\":0,\\\"trackInfo\\\":\\\"/dacu.1.1.6-----scm=1007.18501.117246.0&pvid=pvid&utLogMap=%7B%22x_algo_paras%22%3A%221007.18501.117246.0%3Apvid%3A0%3A%3A0%3A%3A%3Aitem%3Apv%3A___78559%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A%3A0-0-0-0%3A%3A%3A%3A78559-toutiao%23%23v3-toutiao%23%23v3-tce-0-0-0-0%3Ae1e3f2ee-1b15-42b9-bfe1-78cc330e5f25%22%7D-----H46747618\\\",\\\"pvid\\\":\\\"e1e3f2ee-1b15-42b9-bfe1-78cc330e5f25\\\",\\\"ui_id\\\":78559,\\\"scene\\\":\\\"toutiao_v3\\\"}\",\"ui_fields\":\"{}\",\"_pvuuid\":\"e1e3f2ee-1b15-42b9-bfe1-78cc330e5f25\",\"ui_id\":\"78559\"}"}'
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        return sign, parse.quote(data.split("&12574478&")[-1])

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

    def get_have_list(self):
        sql = "select ESSAY_ID from tb_toutiao;"
        self.cur_T.execute(sql)
        self.have_list = [i[0] for i in self.cur_T.fetchall()]

    def requestUrl(self, entityId):
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
            sign, data = self.get_sign(temp, token, entityId)
            url = f'https://h5api.m.taobao.com/h5/mtop.cogman.execute.nologin/1.0/?jsv=2.4.5&appKey=12574478&t={temp}&sign={sign}&api=mtop.cogman.execute.nologin&v=1.0&AntiCreep=true&timeout=5000&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp6&data={data}'
            response = requests.get(url, headers=self.headers, verify=False)
            response_text = response.text[12:-1]
            if "令牌过期" in response_text:
                self.get_cookies(response)
            else:
                break
        info = json.loads(response_text)
        time.sleep(random.randint(5, 20))
        return info

    def handleInfo(self, info):
        self.context = info['data']['context'].replace('"', r'\\\"')
        info_list = info['data']['list']
        result = []
        for item in info_list:
            if item['cardType'] in ['101', "102", '201']:
                if int(item['feed']['id']) not in self.have_list:
                    self.have_list.append(int(item['feed']['id']))
                    print(item['feed']['title'], item['feed']['id'], )
                    images = {"images": []}
                    try:
                        images = {"images": [i['path'] if 'path' in i.keys() else '' for i in item['feed']['element']]}
                    except:
                        traceback.print_exc()
                        print(item)
                    result.append([
                        item['feed']['title'], item['feed']['detailUrl'], json.dumps(images, ensure_ascii=False),
                        int(item['feed']['id']), int(item['feed']['favourCount']),
                        int(item['feed']['readCount']), int(item['feed']['commentCount']), int(item['cardType']), self.findClass(item['feed']['title'])
                    ])

            else:
                if 'feed' in item.keys():
                    print(item['cardType'], item['feed']['detailUrl'])
        self.conn_T.ping(True)
        self.cur_T.executemany(
            'insert into tb_toutiao (TITLE,DETAILURL,IMAGES,ESSAY_ID,FAVOUR,`READ`,COMMENT,CARD_TYPE,CLASSIFY) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);',
            result)
        self.conn_T.commit()

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

    def main(self):
        while True:
            try:
                for key in self.CLASS.keys():
                    self.context = ''
                    for i in range(10):
                        print(key, self.CLASS[key], i + 1)
                        info = self.requestUrl(self.CLASS[key])
                        self.handleInfo(info)
            except:
                traceback.print_exc()
                self.closeSql_T()
                break


def main():
    TT = touTiao()
    TT.get_have_list()
    TT.main()


if __name__ == '__main__':
    main()

