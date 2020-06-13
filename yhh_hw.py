"""
爬取达人有好货达人好物商品
"""
import json
import requests
import CralwerSet.connect_mysql as connect_mysql
import pymysql
import random
import time
import hashlib
from urllib import parse
import CralwerSet.taobao_yhh_recommend as tyr
import re
import traceback

USER_LIST = {
    "悦享优活": "460577576",
    "雅居室": "765800359",
    "不凡设计师": "3192165854",
    "Ulife生活": "3392024392",
    "MrX数码": "2357137617",
}


class YHH_HW(tyr.youHH):
    def get_hw_sign(self, t, token, userid, page):
        """
        执行js，构造sign参数
        :param data:
        :return:
        """
        data = token + "&" + str(
            t) + "&12574478&{\"source\":\"darenhome\",\"type\":\"h5\",\"userId\":\"%s\",\"page\":%s}" % (userid, page)

        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        return sign, parse.quote(data.split("&")[-1])

    def requestHWUrl(self, page, userid):
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
            sign, data = self.get_hw_sign(temp, token, userid, page)
            url = f"https://h5api.m.taobao.com/h5/mtop.taobao.maserati.darenhome.item/1.0/?jsv=2.5.7&appKey=12574478&t={temp}&sign={sign}&api=mtop.taobao.maserati.darenhome.item&v=1.0&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp5&data={data}"
            response = requests.get(url, headers=self.headers,verify=False)
            response_text = response.text[12:-1]
            if "令牌过期" in response_text:
                self.get_cookies(response)
            else:
                break
        info = json.loads(response_text)
        time.sleep(random.randint(5, 20))
        return info['data']['result']['data']['items']

    def handelInfo(self, info):
        cardList = []
        for item in info:
            keys = item.keys()
            if 'itemId' in keys:
                itemId= item['itemId']
            else:
                itemId = 0

            if 'cardType' in keys:
                cardType= item['cardType']
            else:
                cardType = ''

            if 'contentId' in keys:
                contentId= item['contentId']
            else:
                contentId = 0

            if 'contentTitle' in keys:
                contentTitle= item['contentTitle']
            else:
                contentTitle = ''

            if 'contentType' in keys:
                contentType= item['contentType']
            else:
                contentType = ''
            if 'contentUrl' in keys:
                contentUrl= item['contentUrl']
            else:
                contentUrl = ''

            if 'discountPrice' in keys:
                discountPrice= item['discountPrice']
            else:
                discountPrice = 0

            if 'hasCoupon' in keys:
                hasCoupon= item['hasCoupon']
            else:
                hasCoupon = ''

            if 'id' in keys:
                id = item['id']
            else:
                id = ''

            if 'itemImage' in keys:
                itemImage= item['itemImage']
            else:
                itemImage = ''

            if 'price' in keys:
                price= item['price']
            else:
                price = 0

            if 'publishTime' in keys:
                publishTime= item['publishTime']
            else:
                publishTime = 0

            if 'sales' in keys:
                sales= item['sales']
            else:
                sales = 0

            if 'status' in keys:
                status= item['status']
            else:
                status = 0

            if 'title' in keys:
                title= item['title']
            else:
                title = ''

            if 'userId' in keys:
                userId= item['userId']
            else:
                userId = 0

            if int(id) in self.have_list:
                continue
            cardList.append(
                [itemId, cardType, contentId, contentTitle, contentType,
                 contentUrl, discountPrice, hasCoupon,id, itemImage, price,
                 publishTime, sales, status, title, userId])
            print(itemId, contentId, contentTitle, )
            self.have_list.append(int(id))
        return cardList

    def insertCard(self, cardList):
        """
        :param cardList: 文章数据列表
        :return:
        """
        sql = f"""insert into yhh_hw(ITEM_ID, CARDTYPE, CONTENT_ID, CONTENT_TITLE,CONTENT_TYPE,CONTENT_URL,DISCOUNTPRICE,HASCOUPON, CARD_ID,ITEM_IMAGE,PRICE,PUBLISH_TIME,SALES,STATUS,TITLE,USER_ID) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); """
        self.cur_T.executemany(sql, cardList)
        self.conn_T.commit()
        if len(cardList):
            self.users_num[int(cardList[0][-1])] += len(cardList)

    def getHaveList(self):
        """
        获取已存在文章列表
        :return:
        """
        sql = """select CARD_ID from yhh_hw;"""
        self.cur_T.execute(sql)
        result = self.cur_T.fetchall()
        if result:
            for each in result:
                self.have_list.append(int(each[0]))
        sql = "SELECT USER_ID, COUNT(USER_ID) from yhh_hw GROUP BY USER_ID;"
        self.cur_T.execute(sql)
        result = self.cur_T.fetchall()

        for each in result:
            self.users_num[each[0]] = each[1]
        return self.have_list


def main():
    hw = YHH_HW()
    hw.getHaveList()
    try:
        for user in USER_LIST.keys():

            id = USER_LIST[user]
            if hw.users_num[int(id)] > 2000:
                print("用户",id,user,"总条数>2000")
                continue
            page = 1
            while True:
                print('第' + str(page) + '页')
                info = hw.requestHWUrl(page, id)
                cardList = hw.handelInfo(info)
                hw.insertCard(cardList)
                page += 1
                if len(info) == 0 or hw.users_num[int(id)] > 2000:
                    print("用户", user, "总条数>2000或已爬取用户全部信息")
                    break
    except:
        traceback.print_exc()
    hw.closeSql_W()
    hw.closeSql_T()


if __name__ == '__main__':
    main()

