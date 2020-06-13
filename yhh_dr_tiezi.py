import CralwerSet.connect_mysql as connect_mysql
import time
import hashlib
from urllib import parse
import requests
import re
import json
import traceback

HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; xiaomi mix Build/LMY47I; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Safari/537.36 AliApp(TB/9.1.0) TTID/600000@taobao_android_9.1.0 WindVane/8.5.0 900X1600 UT4Aplus/0.2.16",
    "Cookie": "_m_h5_tk=36b5227cd1a1e340e4d56bcc93555f2f_1587526955005; _m_h5_tk_enc=7385708053b9b4519913b71659d347aa;"
}


def read(r):
    """
    读取redis数据
    :param r: redis对象
    :return:
    keys:返回需要处理的数据
    """
    result = r.hgetall('tiezi')
    keys = []
    for each in result.keys():
        if result[each] == b'':
            keys.append(each.decode('utf-8'))
    return keys


def write_value(r, key, value):
    r.hset('tiezi', key, value)


def error_value(r, key):
    r.hset(name="tiezi", key=key, value="12345678910无效value!@#$")


def write_key(r):
    # def write_key(r,page, userid):
    page = 1
    userId = 460577576
    key = str(int(time.time() * 1000)) + "_" + str(page) + "_" + str(userId)
    r.hset('tiezi', key, '')


def get_tiezi_sign(data):
    """
    构造sign参数
    :param data:
    :return:
    """
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return sign, parse.quote(data.split("&")[-1])


def requestTzUrl(temp, page, userid):
    """
    请求页面
    :param
    temp:时间戳
    page:页码
    userid：用户id
    :return:返回页面json数据
    """
    try:
        while True:
            _m_h5_tk, _m_h5_tk_enc = (re.findall('_m_h5_tk=[^;]*', HEADERS['Cookie'])[0].split('=')[1],
                                      re.findall('_m_h5_tk_enc=[^;]*', HEADERS['Cookie'])[0].split('=')[1])
            token = _m_h5_tk.split('_')[0]
            userInfo = ''
            # 获取达人主要信息
            while page == "1":
                data = """%s&%s&12574478&{"source":"youhh_h5","type":"h5","userId":"%s"}""" % (
                    token, temp, userid)
                sign, data = get_tiezi_sign(data)
                url = f"https://h5api.m.taobao.com/h5/mtop.taobao.maserati.darenhome.main/1.0/?jsv=2.5.8&appKey=12574478&t={temp}&sign={sign}&api=mtop.taobao.maserati.darenhome.main&v=1.0&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp2&data={data}"
                response = requests.get(url, headers=HEADERS, verify=False)
                response_text = response.text[12:-1]
                if "令牌过期" in response_text:
                    print("令牌过期")
                    print(response_text)
                    get_cookies(response)
                    continue
                else:
                    print('主页', response_text)
                    user_info = json.loads(response_text)
                    userInfo = user_info['data']['result']['data']['header']
                    break

            temp2 = str(int(temp) + 1)
            data = """%s&%s&12574478&{"source":"youhh_h5","type":"h5","userId":"%s","page":%s,"tab":"10004"}""" % (
                token, temp2, userid, page)
            print('列表data参数', data)
            sign, data = get_tiezi_sign(data)
            url = f"https://h5api.m.taobao.com/h5/mtop.taobao.maserati.darenhome.feed/1.0/?jsv=2.5.8&appKey=12574478&t={temp2}&sign={sign}&api=mtop.taobao.maserati.darenhome.feed&v=1.0&preventFallback=true&type=jsonp&dataType=jsonp&callback=mtopjsonp3&data={data}"
            response = requests.get(url, headers=HEADERS, verify=False)
            response_text = response.text[12:-1]
            # 获取达人帖子列表
            if "令牌过期" in response_text:
                get_cookies(response)
                continue
            else:
                break
        print('列表', response_text)
        info = json.loads(response_text)
        print(info)
        return json.dumps({'data': info['data']['result']['data']['feeds'], 'user': userInfo}, ensure_ascii=False)
    except:
        traceback.print_exc()
        error_value(r, str(temp) + "_" + str(page) + "_" + str(userid))


def get_cookies(response):
    _m_h5_tk = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk'].value
    _m_h5_tk_enc = response.cookies._cookies['.taobao.com']['/']['_m_h5_tk_enc'].value
    cookies = f'_m_h5_tk={_m_h5_tk};_m_h5_tk_enc={_m_h5_tk_enc};'
    HEADERS['Cookie'] = cookies
    return cookies


def main(r):
    while True:
        keys = read(r)
        if keys:
            print("接收到数据")
        for key in keys:
            print('key', key)
            temp, page, userId = key.split("_")
            if not page.isdigit() or not userId.isdigit():
                error_value(r, key)
                continue
            print("时间戳", temp, "页码", page, "用户编号", userId)
            value = requestTzUrl(temp, page, userId)
            if not value:
                time.sleep(0.1)
                continue
            write_value(r, key, value)
            print("处理完成数据", key, value)
        time.sleep(0.1)


if __name__ == '__main__':
    # 主程序
    r = connect_mysql.Redis()
    while True:
        try:
            main(r)
        except:
            traceback.print_exc()
    # 测试
    # data = """4cd2cdec17c026e3292674b9d61cbede&1588044043294&12574478&{"source":"youhh_h5","type":"h5","userId":"460577576","page":1,"tab":"10004"}"""
    #
    # print(get_tiezi_sign(data))
