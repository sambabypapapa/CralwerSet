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

    def get_sign(self, t, token, page, key):
        """
        执行js，构造sign参数
        :param data:
        :return:
        """
        # argue = {
        #     'tce_sid': '1891397',
        #     "tce_vid": "0",
        #     "tid": "",
        #     "tab": "",
        #     "topic": f"{tabId[key][0]}",
        #     "count": "",
        #     "env": "online",
        #     "pageNo": "1",
        #     "psId": "51817",
        #     "bizCode": "steins.goodItem",
        #     "type": "selected_v2",
        #     "page": f"{page}",
        #     "pageSize": "20",
        #     "tabId": f"{tabId[key][1]}",
        #     "contentIds": "2500000222552474145%2C2500000213511536931",
        #     "viewTopicId": "",
        #     "line": "",
        #     "home_clickItemId": "590236412947",
        #     "src": "phone",
        # }
        # argur_string = json.dumps()
        # if page == 1:
        data = token + "&" + str(
            t) + "&12574478&{\"d\":\"{\\\"tce_sid\\\":\\\"1891397\\\",\\\"tce_vid\\\":\\\"0\\\",\\\"tid\\\":\\\"\\\",\\\"tab\\\":\\\"\\\",\\\"topic\\\":\\\"%s\\\",\\\"count\\\":\\\"\\\",\\\"env\\\":\\\"online\\\"," \
                 "\\\"pageNo\\\":\\\"1\\\",\\\"psId\\\":\\\"51817\\\",\\\"bizCode\\\":\\\"steins.goodItem\\\",\\\"type\\\":\\\"selected_v2\\\",\\\"page\\\":\\\"%s\\\",\\\"pageSize\\\":\\\"20\\\",\\\"tabId\\\":\\\"%s\\\"," \
                 "\\\"contentIds\\\":\\\"\\\",\\\"viewTopicId\\\":\\\"\\\",\\\"line\\\":\\\"\\\",\\\"home_clickItemId\\\":\\\"590236412947\\\",\\\"src\\\":\\\"phone\\\"}\"}"%(
            tabId[key][0], str(page), tabId[key][1])
        #                               {"tce_sid":"1891397","tce_vid":"0","topic":"selected_new_1","src":"phone","params":"{\"resId\":\"6696424\",\"bizId\":\"2020\",\"tce_sid\":\"1891397\",\"tce_vid\":\"0\",\"topic\":\"selected_new_1\",\"env\":\"dev\",\"pageNo\":1,\"psId\":\"51817\",\"bizCode\":\"steins.goodItem\",\"type\":\"selected_v2\",\"page\":1,\"pageSize\":20,\"tabId\":\"1\",\"src\":\"phone\",\"columnGray\":false,\"source\":\"tceFaas\"}","isbackup":true,"backupParams":"tce_sid,tce_vid,topic,src","_pvuuid":1589274317877}
        # "curPageUrl":"https%3A%2F%2Fmarket.m.taobao.com%2Fapps%2Fyouhaohuo%2Findex%2Findex4.html%3Futparam%3D%257B%2522ranger_buckets_native%2522%253A%2522tsp2584_22605%2522%257D%26scm%3D1007.home_gongge.youhh.d%26spm%3Da215s.7406091.gongge.d3%26home_clickItemId%3D586112561282%26wh_weex%3Dtrue%26wx_navbar_transparent%3Dtrue%26data_prefetch%3Dtrue%26content_id%3D2500000218901819190%2C2500000213737496494",
        # else:
        # data = token + "&" + str(
        #     t) + "&12574478&{\"d\":\"{\\\"tce_sid\\\":\\\"1891397\\\",\\\"tce_vid\\\":\\\"0\\\",\\\"tid\\\":\\\"\\\",\\\"tab\\\":\\\"\\\",\\\"topic\\\":\\\"%s\\\",\\\"count\\\":\\\"\\\",\\\"env\\\":\\\"online\\\",\\\"pageNo\\\":\\\"1\\\",\\\"psId\\\":\\\"51817\\\",\\\"bizCode\\\":\\\"steins.goodItem\\\",\\\"type\\\":\\\"selected_v2\\\",\\\"page\\\":\\\"%s\\\",\\\"pageSize\\\":\\\"20\\\",\\\"tabId\\\":\\\"%s\\\",\\\"clickedIds\\\":\\\"\\\",\\\"src\\\":\\\"phone\\\"}\"}" % (
        #            tabId[key][0], page, tabId[key][1])
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
        if "photos" in info['data']['models']['content'].keys():
            for photo in info['data']['models']['content']['photos']:
                if 'desc' in photo.keys():
                    print(photo['desc'])
        return info

    def requestUrl(self, page, key):
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
            sign, data = self.get_sign(temp, token, page, key)
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

    def main(self, page, key):
        try:
            info = self.requestUrl(page, key)
            try:
                for each in info['data']['result']['1891397']['result'][0]['data'][0]['data'][0][0]['result']['result']:
                    if each['type'] == '33':
                        contentid = int(each['contentId'])
                        if contentid in self.have_list:
                            continue
                        else:
                            self.have_list.append(contentid)
                            title = each['title']
                            mainClass = self.findClass(title)
                            print(contentid, title, mainClass)
                            self.insertEssay(contentid, title, mainClass)
            except:
                print(info)
            self.conn_T.ping(True)
            self.conn_T.commit()
        except Exception as e:
            if e == "KeyError: 'result'":
                print(info)
            traceback.print_exc()
            return False

        return True


def main():
    yhh = youHH()
    yhh.getHaveList()
    for key in tabId.keys():
        PAGE = 1
        while True:
            print(key, '第' + str(PAGE) + "页")
            result = yhh.main(PAGE, key)
            if not result:
                break
            PAGE += 1
            if PAGE > 50:
                break
    yhh.closeSql_T()
    yhh.closeSql_W()


if __name__ == '__main__':
    tabId = {
        '精选': ["selected_new_0", "0", ],
        '时尚馆': ["selected_new_1", "1", ],
        '电器馆': ["selected_new_7", "7", ],
        '生活馆': ["selected_new_5", "5", ],
        '母婴馆': ["selected_new_4", "4", ],
        '运动馆': ["selected_new_6", "6", ],
        '美妆馆': ["selected_new_2", "2", ],
        '食品馆': ["selected_new_3", "3", ],
        '全球馆': ["selected_new__1", "-1", ],
    }
    main()


#  //ci.xiaohongshu.com/df034c41-4168-559b-8506-501977e24fad?imageView2/2/w/1080/format/jpg
#  //ci.xiaohongshu.com/4d5d8b94-0512-3b3f-929c-0e398c9ecbf9?imageView2/2/w/1080/q/75/format/jpg