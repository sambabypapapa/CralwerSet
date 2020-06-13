"""
在线搜索小红书作者信息
"""

from CralwerSet.xiaohongshu.xiaohs import XHS
xhs = XHS()

# 小红书笔记在线查询

import redis
import json
import requests
import hashlib
from urllib.parse import quote
import CralwerSet.connect_mysql as connect_mysql
import time
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





def get_user_Xsign(keyword, page):
    data = "/fe_api/burdock/weixin/v2/search/users?keyword=%s&page=%s&pageSize=20WSUDD" % (
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
    x_sign = get_Xsign(keyword, page)
    headers['X-sign'] = x_sign
    url = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/notes?keyword=%s&sortBy=general&page=%s&pageSize=20&needGifCover=true" % (
        quote(keyword, 'utf-8'), page)
    response = requests.get(url, headers=headers, verify=False)
    text = response.text
    return text


def requestUser(keyword, page):
    headers = {
        'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
        "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
    }
    x_sign = get_Xsign(keyword, page)
    headers['X-sign'] = x_sign
    url = "https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/search/users?keyword=%s&page=%s&pageSize=20" % (
        quote(keyword, 'utf-8'), page)
    response = requests.get(url, headers=headers, verify=False)
    text = response.text
    return text


def read(r):
    """
    读取redis数据
    :param r: redis对象
    :return:
    keys:返回需要处理的数据
    """
    result = r.hgetall('xhs')
    keys = []
    for each in result.keys():
        if result[each] == b'':
            keys.append(each.decode('utf-8'))
    return keys


def write_value(r, key, value):
    """
    写入数据
    :param r:
    :param key:
    :param value:
    :return:
    """
    r.hset('xhs', key, value.replace('\n', '<br>'))


def error_value(r, key, value):
    """
    报错
    :param r:
    :param key:
    :param value:
    :return:
    """
    r.hset(name="wt", key=key, value=value)


def main():
    while True:
        try:
            r = connect_mysql.Redis()
            while True:
                keys = read(r)
                if not keys:
                    time.sleep(0.1)
                    continue
                for key in keys:
                    print(key)
                    keyword, page, tag, temp = key.split('|')
                    if tag == 'note':
                        print(tag, '= note!')
                        text = request(keyword, page)
                    elif tag == 'user':
                        print(tag, '= user!')
                        text = requestUser(keyword, page)
                    else:
                        text = json.dumps({
                            'code': 1,
                            'success': False,
                            'data': "type err!"
                        })
                    print(text)
                    write_value(r, key, text)
        except:
            traceback.print_exc()



def write_key(r):
    keyword = '美妆情报局'
    page = 1
    t = str(int(time.time() * 1000))
    tag = 'note'
    key = keyword + '|' + str(page) + '|' + tag + "|" + t
    r.hset('xhs', key, '')


if __name__ == '__main__':
    main()