import requests
import json
import time
import traceback
import CralwerSet.connect_mysql as connect_mysql
import datetime


class QianGua():
    def __init__(self):
        self.loginUrl = "http://api.qian-gua.com/login/Login?_="
        self.apiUrl = "http://api.qian-gua.com/v1/Note/GetNoteHotList?_="
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36"
        }
        self.opt = {
            'NoteTags': {
                '彩妆': [83],
                '护肤': [84],
                '洗护香氛': [82],
                '时尚穿搭': [77],
                '美甲': [101],
                '美食饮品': [87],
                '母婴育儿': [93],
                '旅行住宿': [86],
                '健身减肥': [88],
                '星座情感': [95],
                '动漫': [79],
                '萌宠动物': [92],
                '萌娃': [94],
                '影音娱乐': [80],
                '情感两性': [89],
                '科技数码': [96],
                '出行工具': [97],
                '婚嫁': [99],
                '居家生活': [90],
                '教育': [78],
                '摄影': [81],
                '医疗养生': [85],
                '民生资讯': [91],
                '游戏应用': [102],
                '赛事': [100],
                '其他': [76],
            },
            "BloggerProps": {
                "官方号": [8],
                "品牌号": [16],
                "明星": [32],
                "知名KOL": [4],
                "头部达人": [64],
                "腰部达人": [128],
                "初级达人": [256],
                "素人": [512],
            },
            "NoteType": {
                "图文笔记": 'normal',
                "视频笔记": 'video'
            },
            "isBusiness": {
                '是': True,
                '否': False,
            },
            "FansSexType": {
                "女生多数": 2,
                "男生多数": 1,
            },
            "FansGroups": [
                "少男少女",
                "新手宝妈",
                "潮男潮女",
                "轻奢白领",
                "恋爱女生",
                "爱美少女",
                "孕妇妈妈",
                "专注护肤党",
                "爱买彩妆党",
                "网红潮人",
                "追星族",
                "在校大学生",
                "潮男潮女",
                "恋爱青年",
                "时尚潮人",
                "乐活一族",
                "摄影技术控",
                "社交达人",
                "健身男女",
                "瘦身男女",
                "科技生活党",
                "备孕待产",
                "文艺青年",
                "备孕宝妈",
                "工薪阶层",
                "品质吃货",
                "家庭妇女",
                "家有萌娃",
                "老手宝妈",
                "宅男宅女",
                "爱家控",
                "流行男女",
                "学生党",
                "运动控",
                "游戏宅男",
                "医美一族",
                "养生大军",
                "爱车一族",
                "评价吃货",
                "萌宠一族",
                "两性学习",
                "职场新人",
                "中学生",
                "大学生",
                "二次元萌宅",
                "备婚男女",
                "赛事球迷",
                "其他",
            ],
            "SortType": [
                1, 2, 3, 4
            ]
        }
        pass

    def login(self):
        temp = str(int(time.time() * 1000))
        data = {"tel": "15990048082", "pwd": "bscm666"}
        response = requests.post(self.loginUrl + temp, data=data, headers=self.headers)
        self.headers['Cookie'] = "User=" + response.cookies._cookies['.qian-gua.com']['/']['User'].value

    def getData(self):
        print('开始时间', datetime.datetime.now())
        for noteTag in self.opt['NoteTags'].keys():
            for bloggerProp in self.opt['BloggerProps'].keys():
                for noteType in self.opt['NoteType'].keys():
                    for isBusiness in self.opt['isBusiness'].keys():
                        for fansSexType in self.opt['FansSexType'].keys():
                            for fansGroups in self.opt['FansGroups']:
                                for sortType in self.opt['SortType']:
                                    data = {"SortType": sortType, "pageIndex": 1, "pageSize": 200, "Days": -1,
                                            "StartTime": '2020-04-30', "EndTime": '2020-04-30', "NoteTags": noteTag,
                                            "BloggerProps": bloggerProp, "NoteType": noteType, "isBusiness": isBusiness,
                                            "FansSexType": fansSexType, "FansGroups": [fansGroups]}
                                    response = requests.post(self.apiUrl + str(int(time.time() * 1000)),
                                                             headers=self.headers, data=data, verify=False).text
                                    print(response)
        print('结束时间', datetime.datetime.now())


if __name__ == '__main__':
    qg = QianGua()
    qg.login()
    qg.getData()
