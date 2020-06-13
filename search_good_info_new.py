"""
功能：爬取多元化商品池所有商品；
环境：python3
作者：百舸
"""
import requests
import datetime
from requests.packages import urllib3
import json
import CralwerSet.connect_mysql as connect_mysql
import threading
import time
import CralwerSet.schedule as schedule
import pymysql
import CralwerSet.badou_essay_list_crawl as badou_essay_list_crawl


def comment(sc):
    # while True:
    #     try:
    conn = connect_mysql.w_shark_erp()
    cur = conn.cursor()
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}
    isNew7 = False
    while True:
        try:
            info = sc.pop()
        except IndexError:
            cur.close()
            conn.close()
            return

        for i in range(0, 2500, 25):
            url = f'https://kxuan.taobao.com/searchSp.htm?data-key=s&data-value=25&ajax=true&_ksTS=1575682938492_769&callback=jsonp770&ruletype=2&bcoffset=2&navigator=all&nested=we&is_spu=0&1=1&ntoffset=0&s={i}&kxuan_swyt_item=37662&cat={info[0]}&searchtype=item&uniq=pid&id=4525&enginetype=0&bcoffset=2&ntoffset=0'
            while True:
                try:
                    page_text = requests.get(url=url, headers=header, verify=False).text
                    break
                except Exception as e:
                    print(e)
                    continue
            string = page_text.split("(", 1)[1][:-1]
            result = json.loads(string)
            goods = result['mods']['itemlist']['data']['auctions']
            goods_info = []

            for good in goods:
                if int(good['nid']) in have_list:
                    continue
                icon = []
                for each in good['icon']:
                    icon.append({"icon_key":each['icon_key'],"innerText":each['innerText'],"position":each['position']})
                    if each['innerText'] == '营销':
                        isNew7 = True
                have_list.append(int(good['nid']))
                if not isNew7:
                    isNew7 = False
                    continue

                try:
                    sameStyleCount = good['sameStyleCount']
                except KeyError:
                    sameStyleCount = 0
                goods_info.append((info[2], good['nid'], good['raw_title'], good['detail_url'],
                                   good['view_sales'].strip('人付款'), json.dumps(icon, ensure_ascii=False), good['nick'],
                                   good['shopLink'], good['q_score'], good['pic_url'],
                                   good['view_price'], json.dumps(good["shopcard"]), sameStyleCount))

            while True:
                try:
                    sql = "insert into cm_commodity_new (CLASSIFY_ID, URL_ID,TITLE,URL,SALES,CREATE_DATE,ICON,NICK,SHOPLINK,Q_SCORE,PIC_URL,PRICE,SHOPCARD,SAMESTYLECOUNT) values (%s,%s,%s,%s,%s,NOW(),%s,%s,%s,%s,%s,%s,%s,%s);"
                    num = cur.executemany(sql, goods_info)
                    conn.commit()
                    print(info[1], i - 25, '-', i, datetime.datetime.now(), '更新了', num, '条')
                    break
                except pymysql.err.OperationalError:
                    print('由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。')
                    conn.ping(True)

            if len(goods) < 25:
                break
        # except:
        #     continue


if __name__ == '__main__':
    while True:
        try:
            conn = connect_mysql.w_shark_erp()
            cur = conn.cursor()
            sql = "select DISTINCT(URL_ID) from cm_commodity_new;"
            cur.execute(sql)

            have_list = []
            for each in cur.fetchall():
                have_list.append(each[0])
            urllib3.disable_warnings()

            Schedule = schedule.schedule('select distinct(ID),cat,MAIN_ID from class_id order by ID desc;',
                                         connect_mysql.w_shark_erp())

            thread_list = []
            for i in range(6):
                thread_list.append(threading.Thread(target=comment, args=(Schedule,)))
            for thread in thread_list:
                thread.start()
                time.sleep(1)
            for thread in thread_list:
                thread.join()
        except:
            continue

