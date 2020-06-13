import requests
import json
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
import time
import os
import pickle
import datetime
import re
import CralwerSet.connect_mysql as connect_mysql
import Levenshtein
import traceback


class crawl():
    def __init__(self):
        self.conn = connect_mysql.w_shark_erp()
        self.cur = self.conn.cursor()
        self.had_list = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        with open('collect.pk', 'rb') as f:
            self.collect = pickle.load(f)

    def get_goods(self):
        """
        获取要爬取文案的商品
        :return: [url_id, url, title]
        """
        day = str(datetime.datetime.now())[:10]
        print(day)
        self.cur.execute(f'select URL_ID,URL,TITLE from cm_commodity where CREATE_DATE like "{day}%";')
        result = self.cur.fetchall()
        good_list = []
        self.had_list = self.had()
        for each in result:
            if each[0] not in self.had_list:
                good_list.append([each[0], each[1], each[2]])
        return good_list

    def create_driver(self):
        """
        创建一个浏览器
        :return:
        """
        PROXY_PATH = ''.join([os.getcwd(), '\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy.bat'])
        self.server = Server(PROXY_PATH)
        self.server.start()
        self.proxy = self.server.create_proxy()

        chrome_options = Options()
        chrome_options.add_argument('--proxy-server={0}'.format(self.proxy.proxy))
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        # self.driver.set_window_size(1440, 1440)
        self.driver.maximize_window()
        # 设置一个智能等待
        self.waiter = WebDriverWait(self.driver, 5)

    def login(self):
        """
        登录八斗
        :return:
        """
        # 登录页面获取token
        login_url = "https://drbl.daorc.com/login_login.action "
        response = requests.get(login_url, headers=self.headers).text
        token = re.findall('"token":"[^"]*"', response)
        print(token)
        # 发送请求获取参数
        url = "https://drbl.daorc.com/user_jsonLogin.action"
        data = {
            "loginName": "7777754321",
            "password": "7777754321",
            "checkyzm": "0",
            "login_yzm": "",
            "struts.token.name": "token",
            "token": token
        }
        response = response.post(url, data, headers=self.headers)

    def diff(self, string, List):
        """
        文案去重
        :param List:
        :return:
        """
        for each in List:
            if Levenshtein.ratio(string, each[1]) > 0.8:
                return False
        return True

    def write_essay(self, url):
        write_url = 'https://drbl.daorc.com/data_addData.action?fileTypeId=7714&tableFlag=WJ&isopen=0'
        self.driver.get(write_url)
        try:
            self.driver.find_element_by_class_name('layui-layer-btn0').click()
        except:
            pass
        search_good_js = """$.ajax({
    url: "https://drbl.daorc.com/commoditylibrary_getCommodityDetailByUrl.action",
    type: "POST",
    contentType: "application/x-www-form-urlencoded; charset=UTF-8",
    data: JSON.stringify({"url":"%s",'ischannelvalidate':1,'filetypeidxp':{@id@:@4073@,@kxuan_swyt_item@:@32627@,@ischannelvalidate@:@1@},'filedicid':1545825760340})});""" % url
        self.proxy.new_har("brand", options={'captureHeaders': True, 'captureContent': True})
        time.sleep(4)
        self.driver.execute_script(search_good_js)
        result = self.proxy.har
        print(result)

    def handle_keys(self, string):
        """
        :param 需要提取常用词的string:
        :return 常用词列表:
        """
        result = []
        string1 = ''
        i = -1
        while True:
            i += 1
            if i >= len(string):
                break
            string1 += string[i]
            while True:
                try:
                    print(string)
                    cll = self.collect[string[i]]
                except KeyError:
                    i += 1
                    continue
                except IndexError:
                    result.append(string1)
                    return result
                i += 1
                if i >= len(string):
                    if len(string1) > 1:
                        result.append(string1)
                    string1 = ''
                    i -= 1
                    break
                if string[i] == ' ' or string[i] not in cll.keys() or cll[string[i]] < 110:
                    if len(string1.strip(' ')) > 1:
                        result.append(string1)
                    string1 = ''
                    i -= 1
                    break
                else:
                    string1 += string[i]
        print(result)
        return result

    def byUrlQueryWord(self, id, good_url, title):
        """输入输入商品链接及关键字并搜索
            返回文案列表"""
        temp = int(time.time() * 1000)
        self.headers[
            'Referer'] = f"https://drbl.daorc.com/picturelibrary_getParagraphView.action?standard=1&min_h=500&min_w=500&title=&describe=&url=&type=&itemId={id}&bname=&typename=%E6%A8%A1%E5%9D%97&isopen=1&temp=1587447754600"
        url = "https://down.daorc.com/main_welcome2.action?set=11"
        data = {
            "url": "https:" + good_url,
            "title": title,
            "filetypeid": "7715",
        }
        response = requests.post(url, data, headers=self.headers,verify=False).text
        data = json.loads(response)
        argum = []
        for each in data['data']:
            if len(each['summary']) >= 50 and self.diff(each['summary'], argum) and self.excludeWord(each['summary']):
                if 70 <= len(each['summary']) <= 75 and each['summary'][-1:] not in ['。', '！', '？', '”', '.']:
                    continue
                argum.append([id, each['summary']])
                print(id, each['summary'])
        return argum

    def queryWord(self, id, good_url, title):
        """输入输入商品链接及关键字并搜索
            返回文案列表"""
        temp = int(time.time() * 1000)
        self.headers[
            'Referer'] = "https://drbl.daorc.com/picturelibrary_getParagraphView.action?standard=1&min_h=500&min_w=500&title=&describe=&url=&type=&itemId=&bname=&typename=%E6%A8%A1%E5%9D%97&isopen=1&temp=1587447754600"
        url = "https://down.daorc.com/main_welcome2.action?set=getContentReason"
        data = {
            "contentKeyWords":title,
        }
        response = requests.post(url, data, headers=self.headers).text
        data = json.loads(response)
        argum = []
        for each in data['data']:
            if len(each['summary']) >= 50 and self.diff(each['summary'], argum) and self.excludeWord(each['summary']):
                if 60 <= len(each['summary']) <= 90 and each['summary'][-1:] not in ['。', '！', '？', '”', '.','~',]:
                    print('字节长度', len(each['summary'].encode()))
                    continue
                argum.append([id, each['summary']])
                print(id, each['summary'])
        return argum

    def insert_text(self, essays):
        sql = "insert into cm_text (URL_ID,TEXT) values (%s,%s);"
        num = self.cur.executemany(sql, essays)
        self.conn.commit()
        print(f'{str(datetime.datetime.now())}插入了{num}条')

    def had(self):
        sql = f'select distinct URL_ID from cm_text where URL_ID is not null;'
        self.cur.execute(sql)
        had_list = []
        result = self.cur.fetchall()
        if result:
            for each in result:
                had_list.append(each[0])
        return had_list

    def excludeWord(self, string):
        """
        排除敏感词
        :param string:
        :return:
        """
        expect_words = [
            '2015', '2016', '2017', '2018', '2014', '优惠', '涨价', '促销', '新款', '第二件', '全场', '购买', '包邮',
            '特惠 ', '折', '直供', '热卖', '爆款', '上新', '抢', '折扣', '打折', '毛泽东', '邓小平', '习近平', 'com', 'cn', 'net',
            '原价', '拍下', '限购', '特价', '元', '限时', "邮政", "顺丰", "圆通", "中通", "菜鸟驿站", "EMS", "ems", "快递",
            "申通", "下单", "购买", "编辑部", 'COM', "编辑", "<br>", '天无理由','不计成本','欧范小姐',
        ]
        for each in expect_words:
            if each in string:
                return False
        return True


if __name__ == '__main__':
    # 爬取八斗文案
    Crawl = crawl()
    while True:
        try:
            for good in Crawl.get_goods():
                text = Crawl.byUrlQueryWord(good[0], good[1], good[2], )
                Crawl.insert_text(text)
        except:
            traceback.print_exc()
            break
    Crawl.cur.close()
    Crawl.conn.close()

