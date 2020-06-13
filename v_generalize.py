import CralwerSet.connect_mysql as connect_mysql
import json
import requests
import datetime
import time
import random
import easygui as g

headers = {
    "Connection": "keep-alive",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36",
    "Referer":"https://v.taobao.com/v/content/video",
    "Cookie":"XSRF-TOKEN=9400fddf-8598-4fe7-9fa3-dc158ab982ff; _samesite_flag_=true; cookie2=174889f3da4383bb0b69df16e0d6d56c; t=d7e3737e54a72cd41a95478fff278ba5; _tb_token_=eee95e1d3df63; mt=ci=0_0; _tb_token_=undefined; cna=q04hFywZ7RICARsSAqAKxEjR; lgc=%5Cu70B8%5Cu4E86%5Cu8FD9%5Cu4E2A%5Cu987A%5Cu5B50; dnk=%5Cu70B8%5Cu4E86%5Cu8FD9%5Cu4E2A%5Cu987A%5Cu5B50; tracknick=%5Cu70B8%5Cu4E86%5Cu8FD9%5Cu4E2A%5Cu987A%5Cu5B50; v=0; _m_h5_tk=eb98b46edbf0bb2f43580408f3321695_1587384966546; _m_h5_tk_enc=be8a1a51bed44411dc19010cb31c3aba; sgcookie=EuO9eIaAj2jvmbxslXOrh; unb=2632081012; uc1=cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie21=U%2BGCWk%2F7p4mBoUyS4E9C&cookie14=UoTUPcii%2FmjRow%3D%3D; uc3=lg2=VFC%2FuZ9ayeYq2g%3D%3D&vt3=F8dBxGR3%2Fy6ovWHlpkc%3D&id2=UU6ifpqosHikVg%3D%3D&nk2=trmexKP205X9gFOH; csg=64ac8e0b; cookie17=UU6ifpqosHikVg%3D%3D; skt=b9005a62c4da2232; existShop=MTU4NzQzMTMwOA%3D%3D; uc4=id4=0%40U2xvKj8ULbTw1mnLTZg9YIuSQtuT&nk4=0%40tG90if0DnSIUfEG6Q6BlICjDd9hLfEg%3D; _cc_=UIHiLt3xSw%3D%3D; _l_g_=Ug%3D%3D; sg=%E5%AD%9023; _nk_=%5Cu70B8%5Cu4E86%5Cu8FD9%5Cu4E2A%5Cu987A%5Cu5B50; cookie1=BxeMfJ%2BF4RC08j%2BX%2BZGN7ugGUx4l6KH8Y%2F3xcgGclP0%3D; tfstk=cjfABAZxeuqD_C_2L1ek1Rf3XiF1a_r9Vqti6PMFPrtZuRlEtsv5t65MI-TsDQUR.; l=eB_BNnkVqZnX0ihUBO5ZS5TbU7_tNIRb8sPrfdJgmIHca69F_nSbdNQcLdZy8dtjgt5A8eKz8-EPGdeWSWz38xtjopgDAI4kCZv68e1..; isg=BCEhG87N225oGXS_a7TE0Z7VMO07zpXAvGxsuoP2uCjG6kC8yh2PkWdsSB7sIi34",
}
sql = """insert into v_video(USER_ID,NICK,PIC_URL,HOME_URL,FANS,`READS`,CLASS,UPDATE_TIME) values(%s,%s,%s,%s,%s,%s,%s,now());"""
update_sql = """update v_video set FANS=%s,`READS`=%s,UPDATE_TIME=now() where USER_ID=%s"""
conn = connect_mysql.test()
cur = conn.cursor()
select_sql = """select USER_ID from v_video;"""
cur.execute(select_sql)
had_list = []
for each in cur.fetchall():
    had_list.append(each[0])


for i in range(1,26):
    print("第",i,"页")
    url = f"https://v.taobao.com/micromission/req/selectCreatorV3.do?cateType=602&currentPage={i}"
    while True:
        try:
            response = requests.get(url, headers=headers, verify=False).text
            data = json.loads(response)
            result = data['data']['result']
            break
        except KeyError:
            cookie = g.enterbox(msg="请进行人机验证，并输入新cookie",title="警告！")
            print(cookie)
            headers['Cookie'] = cookie
    user_list = []
    update_user_list = []
    for each in result:
        userId = each['userId']
        nick = each['nick']
        picUrl = each['picUrl']
        homeUrl = each['homeUrl']
        servType = each['servType']
        fansCount = each['fansCount']
        reads = ''
        for title in each['titleArray']:
            if "7日" in title['name']:
                reads = title['value'][0:-1]

                try:
                    if float(reads) < 100:
                        reads = False
                except ValueError:
                    print(reads)
        if not reads:
            continue
        if userId in had_list:
            update_user_list.append([fansCount,reads,userId])
        else:
            had_list.append(userId)
            user_list.append([userId,nick,picUrl,homeUrl,fansCount,reads,servType])
    cur.executemany(sql, user_list)
    cur.executemany(update_sql, update_user_list)
    conn.commit()
    time.sleep(random.randint(5,20))
cur.close()
conn.close()

