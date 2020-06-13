# 小红书笔记在线查询

import redis
import json
import requests
import hashlib
from urllib.parse import quote
import CralwerSet.connect_mysql as connect_mysql




def get_Xsign(keyword, page):
    data = "/fe_api/burdock/weixin/v2/search/notes?keyword=%s&sortBy=general&page=%s&pageSize=40&needGifCover=trueWSUDD" % (
        quote(keyword, 'utf-8'), page)
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()

    return "X" + sign


def request(keyword, page):
    headers = {
        'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
        "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
    }
    x_sign = get_Xsign(keyword,page)
    print(x_sign)
    headers['X-sign'] = x_sign
    url = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes?keyword=%s&sortBy=general&page=%s&pageSize=40&needGifCover=true"%(quote(keyword, 'utf-8'),page)
    print(url)
    response = requests.get(url,headers=headers,verify=False)
    text = response.text
    return text



if __name__ == '__main__':
    text = request('美妆情报局',1,)
    print(text)


# https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes?keyword=%E7%BE%8E%E5%A6%86%E6%83%85%E6%8A%A5%E5%B1%80&sortBy=general&page=1&pageSize=20&needGifCover=true
# https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes?keyword=%E7%BE%8E%E5%A6%86%E6%83%85%E6%8A%A5%E5%B1%80&sortBy=general&page=1&pageSize=20&needGifCover=true