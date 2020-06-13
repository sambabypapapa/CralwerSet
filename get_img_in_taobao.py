import re
import requests
import CralwerSet.connect_mysql as connect_mysql
import threading
import CralwerSet.schedule as schedule
import time
import datetime
import json
from requests.packages import urllib3

urllib3.disable_warnings()


class mythread(threading.Thread):
    def __init__(self, name, sc):
        threading.Thread.__init__(self)
        self.name = name
        self.obj = sc

    def run(self):
        daemon(self.name, self.obj)




def get_imgs(url):
    while True:
        try:
            response = requests.get(url, headers=headers, verify=False).text
            result = json.loads(response)
            img_list = result['data']['item']['images'][:5]
            break
        except KeyError:
            print(url)
            print("网页请求失败")
            return True, False, True
        except:
            print('重新访问。。。')
            time.sleep(500)
    imgs = json.dumps(img_list)
    popularity = int(result['data']['item']['favcount'])

    evaluates = result['data']['seller']['evaluates']
    grade = {}
    for each in evaluates:
        # 判断评分是否满足要求
        if float(each['score']) < 4.6:
            return False, False, False
        if each['title'] == '宝贝描述':
            title = 'bb'
        elif each['title'] == '卖家服务':
            title = 'mj'
        else:
            title = 'wl'
        grade[title] = each['score']
    return imgs, popularity, json.dumps(grade)


def daemon(name, sc):
    conn_t = connect_mysql.w_shark_erp()
    cur_t = conn_t.cursor()
    while True:
        try:
            info = sc.pop()
        except IndexError as e:
            print(e)
            return
        url = f"https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{info[0]}%22%7D"
        imgs, popularity, grade = get_imgs(url)
        if not imgs:
            print(print(info[0]),'不符合条件')
            sql = f"""update cm_commodity set NEED=2 where URL_ID={info[0]} limit 1;"""
            continue
        elif imgs and not popularity and grade:
            continue
        else:
            print('符合条件')
            # sql = f"""update cm_commodity set IMG_URL='{imgs}',POPULARITY={popularity},GRADE='{grade}', NEED=1 where URL_ID={info[0]} limit 1;"""
            sql = f"""update cm_commodity set IMG_URL='{imgs}',POPULARITY={popularity},GRADE='{grade}' where URL_ID={info[0]} limit 1;"""
        conn_t.ping(True)
        cur_t.execute(sql)
        conn_t.commit()


def main():
    while True:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36',
            }
            sql = "select URL_ID from cm_commodity where NEED<>2 AND CREATE_DATE >= '2019-11-28' AND IMG_URL is null order by CREATE_DATE DESC;"
            Schedule = schedule.schedule(sql, )
            thread_list = []
            for i in range(10):
                thread_list.append(mythread(str(i + 1), Schedule, ))

            for thread in thread_list:
                thread.start()
        except:
            pass
        time.sleep(600)


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36',
    }
    sql = "select URL_ID from cm_commodity where CREATE_DATE >= date_sub(now(),interval 2 day) AND IMG_URL is null order by CREATE_DATE DESC limit 10;"
    while True:
        try:
            Schedule = schedule.schedule(sql, connect_mysql.w_shark_erp())
            thread_list = []
            for i in range(1):
                thread_list.append(mythread(str(i + 1), Schedule, ))

            for thread in thread_list:
                thread.start()
                time.sleep(1)
            while True:
                if not len(Schedule.classes):
                    print("新一轮数据更新")
                    break
                else:
                    time.sleep(6)
                    continue
        except:
            print("程序报错，重新开始")
            pass
