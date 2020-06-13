"""
微淘搜索
"""
import redis
import CralwerSet.connect_mysql as connect_mysql
import requests
from urllib import parse
import json
import re
from bs4 import BeautifulSoup
import traceback
import time as t
import hashlib

HEADER = {
    "User-Agent": "PostmanRuntime/7.20.1"}


def weibo(url):
    try:
        id = max(re.findall("\d+", url))
        detail_url = f"https://m.weibo.cn/status/{id}"
    except:
        traceback.print_exc()
        return 401, '链接解析失败'
    try:
        detail_response = requests.get(url=detail_url, headers=HEADER, verify=False).text
        split_text = re.findall('"pics": [^]]+]', detail_response)[0].replace("\\n", '').replace("\n", '').replace(" ",
                                                                                                                   '')

        text = "{" + split_text + "}"
        text_list = json.loads(text)
        img_list = []
        for text in text_list["pics"]:
            img = text['large']['url']
            img_list.append(img)
        text_url = f"https://m.weibo.cn/statuses/extend?id={id}"
        text_response = requests.get(text_url, verify=False).text
        text_dict = json.loads(text_response)
        content = text_dict['data']['longTextContent']
        text_list = re.findall('[^<>\'"&;:?=/\-#]+', content)
        while True:
            text = max(text_list, key=len)[1:]
            if len(text.replace('%', '')) / len(text) * 100 < 80:
                text_list.remove(max(text_list, key=len))
            else:
                break
        return img_list, text
    except:
        traceback.print_exc()
        return 402, '页面请求失败'


def xiaohongshu(url):
    def get_Xsign(id):
        data = f"/fe_api/burdock/weixin/v2/note/{id}/single_feed?sid=session.1577714043741394419362WSUDD"
        m = hashlib.md5(data.encode())
        sign = m.hexdigest()
        return "X" + sign

    try:
        if "http" != url[: 4]:
            url = re.findall("http[^，]*", url)[0]
            response = requests.get(url, headers=HEADER, verify=False)
            url = response.url
            id = re.findall("/[^/?]*\?", url)[0][1:-1]
        else:
            id = url.split("/")[-1]
        print(id)
    except:
        traceback.print_exc()
        print(url)
        return '401', '链接解析错误'

    url = f"https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/note/{id}/single_feed?sid=session.1577714043741394419362"
    headers = {
        'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
        "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
        "x-sign": get_Xsign(id)
    }
    request_time = 0
    try:
        while 1:
            try:
                response = requests.get(url, headers=headers, verify=False)
                break
            except:
                if request_time > 20:
                    break
                request_time += 1
                continue
        content = response.text
        info = json.loads(content)
        text = info['data']['desc']
        img = [item['url'] for item in info['data']['imageList']]
        print(img, text)
        return img, text
    except:
        traceback.print_exc()
        return '402', '页面请求失败'


def weitao(url):
    try:
        HEADER["Cookie"] = ''
        print(url)
        if "&contentId=" not in url:
            url = re.findall('http[^\s]*', url)[0]
            response1 = requests.get(url, headers=HEADER, verify=False).text
            id = re.findall("&contentId=[^&]*", response1)[0].split('=')[1]
        else:
            id = re.findall("&contentId=[^&]*", url)[0].split('=')[1]
        url = f"https://detail.alicdn.com/getContentDetailByIdV2_{id}_weitao_2017_cover_h5"
    except:
        traceback.print_exc()
        return 401, '链接解析失败'
    try:
        r = requests.get(url, headers=HEADER, verify=False)
        r.encoding = 'utf-8'
        info = json.loads(r.text)
        img_list = []
        for each in info['data']['models']['content']['anchorNew']:
            img_list.append("http:" + each['picture']["picUrl"])
        for each in info['data']['models']['content']['drawerList']:
            img_list.append("http:" + each['itemCoverPic']['picUrl'])
        text = info['data']['models']['content']['summary']
        return img_list, text
    except:
        traceback.print_exc()
        return 402, '页面请求失败'


def kaola(url):
    try:
        id = re.findall('/[^/?]*html\?', url)[0][1: -6]
        url = f"https://zone.kaola.com/idea/{id}.html"
        print(url)
    except:
        traceback.print_exc()
        return 401, '链接解析失败'
    HEADER["Cookie"] = ""
    try:
        response = requests.get(url, headers=HEADER, verify=False).text
        string = re.findall('__INITIAL_STATE.*\);', response)[0][32:-3].replace("\\", "")

        data = json.loads(string)
        imgList = data['ideaDetail']['imgList']
        text = data['ideaDetail']['desc']
        return imgList, text
    except:
        traceback.print_exc()
        return 402, '页面请求失败'


def read(r):
    """
    读取redis数据
    :param r: redis对象
    :return:
    keys:返回需要处理的数据
    """
    result = r.hgetall('wt')
    keys = []
    for each in result.keys():
        if result[each] == b'':
            keys.append(each.decode('utf-8'))
    return keys


def write_value(r, key, value):
    r.hset('wt', key, value.replace('\n', '<br>'))


def error_value(r, key, value):
    r.hset(name="wt", key=key, value="12345678910无效value!@#$")


def write_key(r):
    page = 1
    userId = 460577576
    key = str(int(t.time() * 1000)) + "_" + str(page) + "_" + str(userId)
    r.hset('wt', key, '')


if __name__ == "__main__":
    while True:
        try:
            r = connect_mysql.Redis()
            while True:
                keys = read(r)
                if not keys:
                    t.sleep(0.1)
                    continue
                print(keys)
                for key in keys:
                    url_list, text = '', ''
                    """type 1:weibo;2:weitao;3:kaola;4:xhs"""
                    time, classify, info = key.split("|")

                    if int(classify) == 1:
                        url_list, text = weibo(info)
                    elif int(classify) == 2:
                        url_list, text = weitao(info)
                    elif int(classify) == 3:
                        url_list, text = kaola(info)
                    else:
                        url_list, text = xiaohongshu(info)

                    data_dic = {
                        'urlList': url_list,
                        "text": text
                    }
                    data = json.dumps(data_dic, ensure_ascii=False)
                    print(data)
                    write_value(r, key, data)
        except:
            traceback.print_exc()


