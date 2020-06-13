import requests
import hashlib
import json
import time
import CralwerSet.tb_toutiao as tb_toutiao
import random
import traceback
from CralwerSet.xiaohongshu import xiaohs_user as user

types = {
    "推荐": "homefeed_recommend",
    "时尚": "homefeed.fashion_v2",
    "护肤": "homefeed.skincare_v2",
    "彩妆": "homefeed.cosmetics_v2",
    "美食": "homefeed.food_v2",
    "旅行": "homefeed.travel_v2",
    "影视": "homefeed.movies_v2",
    "读书": "homefeed.books_v2",
    "明星": "homefeed.celebrities_v2",
    "健身": "homefeed.fitness_v2",
    "家居": "homefeed.home_v2",
    "宠物": "homefeed.pets_v2",
    "音乐": "homefeed.music_v2",
    "婚礼": "homefeed.weddings_v2",
    "母婴": "homefeed.maternity_v2",
    "萌娃": "homefeed.baby_v2",
    "数码": "homefeed.digital_v2",
    "汽车": "homefeed.car_v2",
    "男士穿搭": "homefeed.mens_fashion_v2",
}


class XHS():
    def __init__(self):
        self.headers = {
            'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
            "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
        }
        self.fe_api = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/homefeed/personalNotes?category=%s&cursorScore=%s&geo=&page=%s&pageSize=20&needGifCover=true&sid=session.1577714043741394419362"
        self.tt = tb_toutiao.touTiao()
        self.have = []
        self.have_user = []
        self.start = time.time()
        self.request_num = 0
        self.cursorScore = 0

    def get_Xsign(self, category, page, cursorScore):
        data = "/fe_api/burdock/weixin/v2/homefeed/personalNotes?category=%s&cursorScore=%s&geo=&page=%s&pageSize=20&needGifCover=true&sid=session.1577714043741394419362WSUDD" % (
            category, cursorScore, page)
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        self.headers['X-sign'] = "X" + sign
        return "X" + sign

    def request(self, page, cursorScore, key):
        print("sign", self.get_Xsign(types[key], page, cursorScore))
        print('url', self.fe_api % (types[key], cursorScore, page))
        # 获取数据
        response = requests.get(self.fe_api % (types[key], cursorScore, page), headers=self.headers,
                                verify=False).text
        self.request_num += 1
        time.sleep(random.randint(0, 15))
        data = json.loads(response)
        try:
            if not data['data']:
                return False
        except:
            if data['success'] == False and data['msg'] == 'rpc timeout':
                return True

            print(f"耗时{time.time() - self.start}秒，共访问{self.request_num}次")
            print(data)
            if data['code'] == -4613:
                time.sleep(60)
                return False
        # 解析数据
        info, no_user = self.handleDate(data, key)
        # 保存数据
        self.updateData(info, no_user)
        if len(data['data']) < 20:
            return False
        else:
            return True

    def had(self):
        sql = "select distinct NOTE_ID from xhs_note;"
        self.tt.cur_T.execute(sql)
        self.have = [item[0] for item in self.tt.cur_T.fetchall()]

        sql = "select USER_ID from xhs_user;"
        self.tt.cur_T.execute(sql)
        self.have_user = [item[0] for item in self.tt.cur_T.fetchall()]

    def handleDate(self, data, key):
        info = []
        no_user = []
        self.cursorScore = data['data'][-1]['cursorScore']
        try:
            for item in data['data']:
                try:
                    if (item['id']) not in self.have and item['likes'] >= 100:
                        self.have.append(item['id'])
                        print("笔记", item['id'])
                        info.append([
                            item['id'], item['title'], item['type'], item['likes'], item['cover']['url'],
                            item['user']['id'],
                            item['cursorScore'], key
                        ])
                        if item['user']['id'] not in self.have_user:
                            print('用户', item['user']['id'])
                            data = user.getData(item['user']['id'])
                            self.request_num += 1
                            self.have_user.append(item['user']['id'])
                            no_user.append([
                                               item['user']['id'], item['user']['image'], item['user']['nickname'],
                                               item['user']['redOfficialVerifyType'],
                                               item['user']['redOfficialVerifyShowIcon'],
                                               item['user']['officialVerified']
                                           ] + data[:-1])
                except:
                    traceback.print_exc()
                    continue
        except:
            if data['success'] == False and data['msg'] == 'rpc timeout':
                return [], []
            print(f"耗时{time.time() - self.start}秒，共访问{self.request_num}次")
            print(data)
        return info, no_user

    def updateData(self, info, user):
        sql = "insert into xhs_note(NOTE_ID,TITLE,`TYPE`,LIKES,COVER,`USER`,CURSORSCORE,CLASSIFY,`UPDATE_DATE`) values (%s,%s,%s,%s,%s,%s,%s,%s,CURDATE());"
        self.tt.conn_T.ping(True)
        self.tt.cur_T.executemany(sql, info)
        sql = "insert into xhs_user(USER_ID,IMAGE,`NICK_NAME`,RED_OFFICIAL_VERIFY_TYPE,RED_OFFICIAL_VERIFY_SHOW_ICON,`OFFICIAL_VERIFIED`,`UPDATE_DATE`,FOLLOW,FANS,LIKED,COLLECT,LOCATION,`LEVEL`,NOTES) values (%s,%s,%s,%s,%s,%s,CURDATE(),%s,%s,%s,%s,%s,%s,%s);"
        self.tt.conn_T.ping(True)
        self.tt.cur_T.executemany(sql, user)
        self.tt.conn_T.commit()


def main():
    xhs = XHS()
    xhs.had()
    try:
        LIST = [item for item in types.keys()]
        LIST.reverse()
        while True:
            for key in LIST:
                xhs.cursorScore = ''
                for i in range(1, 51):
                    print(key, f"第{i}页")
                    result = xhs.request(i, xhs.cursorScore, key)
                    if not result:
                        break
    except:
        traceback.print_exc()
        xhs.tt.closeSql_T()
        xhs.tt.closeSql_W()


def test_sign():
    xhs = XHS()
    print(xhs.get_Xsign("homefeed_recommend", 15, 1588845586.8800087))


if __name__ == '__main__':
    main()
