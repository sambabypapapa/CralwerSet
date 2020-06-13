import CralwerSet.connect_mysql as connect_mysql
import json
import hashlib
import time
import requests
import random
import traceback




def get_Xsign(id):
    data = f"/fe_api/burdock/weixin/v2/user/{id}?sid=session.1577714043741394419362WSUDD"
    m = hashlib.md5(data.encode())
    sign = m.hexdigest()
    return "X" + sign


def getData(id):
    headers = {
        'device-fingerprint': 'WHJMrwNw1k/HHeHdJP9eciZQM1EIuxb06bdwsL2b8Thw5qsGHcWmXEi2/NlTzrKoNtHPzOLrvAPQmwetCdCyPX5EzFGRDVy4fdCW1tldyDzmauSxIJm5Txg==1487582755342',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm32',
        "authorization": "01fb7d4a-37d8-4b4b-97d4-9bb9f977421c",
        "x-sign": get_Xsign(id)
    }
    url = f"https://www.xiaohongshu.com/fe_api/burdock/weixin/v2/user/{id}?sid=session.1577714043741394419362"
    response = requests.get(url, headers=headers, verify=False)
    # 随机等待
    time.sleep(random.randint(0, 10))
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
    return data


def update(data, cur):
    sql = "update xhs_user set FOLLOW=%s,FANS=%s,LIKED=%s,COLLECT=%s,LOCATION=%s,`LEVEL`=%s,NOTES=%s,UPDATE_DATE=CURDATE() where USER_ID=%s limit 1;"
    cur.execute(sql, data)
    return


if __name__ == '__main__':
    conn = connect_mysql.test()
    cur = conn.cursor()
    sql = 'select USER_ID from xhs_user where NOTES=0;'
    cur.execute(sql)
    for id in [i[0] for i in cur.fetchall()]:
        try:
            data = getData(id)
            conn.ping(True)
            update(data, cur)
            conn.commit()
        except:
            cur.close()
            conn.close()
            traceback.print_exc()
        time.sleep(random.randint(0, 30))
    cur.close()
    conn.close()

