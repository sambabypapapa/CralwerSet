"""
更新关注用户信息
"""
import CralwerSet.connect_mysql as connect_mysql
import json
import hashlib
import time
import requests
import random
import traceback
from CralwerSet.xiaohongshu import xhs_user_trend


def get_Xsign(id):
    data = f"/fe_api/burdock/weixin/v2/user/{id}?sid=session.1577714043741394419362WSUDD"
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return "X" + sign


def getData(id, key):
    headers = {
        'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
        "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
        "x-sign": get_Xsign(id)
    }
    url = f"https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/{id}?sid=session.1577714043741394419362"
    response = requests.get(url, headers=headers, verify=False)
    content = response.text
    info = json.loads(content)
    follow = info['data']['follows']
    fans = info['data']['fans']
    liked = info['data']['liked']
    collect = info['data']['collected']
    location = info['data']['location']
    level = json.dumps(info['data']['level'], ensure_ascii=False)
    notes = info['data']["notes"]
    data = [follow, fans, liked, collect, location, level, notes, id]
    data1 = [key, fans, liked, collect, notes]
    return data, data1


def update(data, data1, cur):
    sql = "update xhs_user set FOLLOW=%s,FANS=%s,LIKED=%s,COLLECT=%s,LOCATION=%s,`LEVEL`=%s,NOTES=%s,UPDATE_DATE=CURDATE() where USER_ID=%s limit 1;"
    conn.ping(True)
    cur.execute(sql, data)
    sql = "insert into xhs_attention_user(USER_KEY,UPDATE_DATE,FANS,LIKED,COLLECT,NOTES) values (%s,curdate(),%s,%s,%s,%s);"
    conn.ping(True)
    cur.execute(sql, data1)
    return


if __name__ == '__main__':
    conn = connect_mysql.test()
    cur = conn.cursor()
    sql = 'select USER_ID,ID from xhs_user where ATTENTION=1 and UPDATE_DATE < CURDATE();'
    while True:
        try:
            conn.ping(True)
            cur.execute(sql)
            for id, key in [i for i in cur.fetchall()]:
                data, data1 = getData(id, key)
                conn.ping(True)
                update(data, data1, cur)
                conn.commit()

                time.sleep(random.randint(0, 40))
            xhs_user_trend.main()
        except:
            conn = connect_mysql.test()
            cur = conn.cursor()
        time.sleep(3600*20)
