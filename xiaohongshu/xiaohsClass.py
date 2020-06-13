"""
一个小红书的类
用户调用小红书微信小程序api的爬虫
"""
import requests
import time
import json
import random
import traceback
import hashlib

class xhs():
    def __init__(self):
        # 小红书账户请求头
        self.headers = {
            'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
            "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
        }
        # 小红书笔记的类型
        self.types = {
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
        # 连接mysql
        self.conn = None
        # 已爬取的笔记列表
        self.hadNote = []
        # 已爬取的作者列表
        self.hadUser = []
        # 对象创建时间
        self.start = time.time()
        # 请求次数
        self.request_num = 0
        # 笔记列表标记
        self.cursorScore = 0

        # 获取笔记列表接口（category=types[i],cursorScore=self.cursorScore,page is int,）
        self.noteListApi = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/homefeed/personalNotes?category=%s&cursorScore=%s&geo=&page=%s&pageSize=20&needGifCover=true&sid=session.1577714043741394419362'
        # 获取笔记详情接口                                                            note's ID
        self.noteDetailApi = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/%s/single_feed?sid=session.1577714043741394419362'
        # 获取作者详情接口                                                       user's ID
        self.userApi = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/%s?sid=session.1577714043741394419362'
        # 通过关键字搜索笔记接口                                                                        searched keyword
        self.searchNoteApi = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes?keyword=%s&sortBy=general&page=%s&pageSize=40&needGifCover=true'
        # 通过关键字搜索作者接口                                                                     searched keyword
        self.searchUserApi = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/users?keyword=%s&page=1&pageSize=20'
        # 通过作者ID搜索该作者笔记列表接口                                                      ID            int
        self.searchNoteApiOfUser = 'https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/%s/notes?page=%s&page_size=15'
        # 关注作者  POST请求                                                                   User ID
        self.followUserApi = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/%s/follow"

    def get_Xsign(self, url):
        data = url[27:] + "WSUDD"
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        self.headers['X-sign'] = "X" + sign
        return "X" + sign

    def getData(self,url):
        self.get_Xsign(url)
        response = requests.get(url, headers=self.headers, verify=False)
        content = response.text
        return content

