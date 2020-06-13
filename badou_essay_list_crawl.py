# 功能：爬取八斗作品库, 获取八斗文案
# 环境：Python3
# 作者：百舸
import requests
import pymysql
import json
import re
import datetime
import threading
import time
import CralwerSet.connect_mysql as connect_mysql
import CralwerSet.schedule as schedule
import sys
from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class mythread(threading.Thread):
    def __init__(self, name, sc):
        threading.Thread.__init__(self)
        self.name = name
        self.obj = sc

    def run(self):
        get_text(self.name, self.obj)


TYPES = {
    "汽车": ['改装发烧友', '爱车一族'],
    "母婴": ['小小公主范', '小小厨师', '我是小医生', '彩绘师', '小小摄影师', '芭比收藏家', '萌宝游乐园', '小小工程师', '早教专家', '小小舞者', '小小运动员', '独立小萌宝',
           '月子女王', '模型控', '宝宝营养师', '萌宝学院', '萌宝逛世界', '小小二次元', '小小军事迷', '天才科学家', '新生萌宝', '海派妈咪', '家有萌娃'],
    "旅游": ['海派甜心', '旅行家'],
    "摄影": ['摄影发烧友'],
    "居家": ['懒癌患者', '抗霾卫士', '温暖小贴士', '香氛控', '古典匠人', '陶艺大师', '盘子控', '工业风的家', '收纳控', '水族爱好者', '杯子控', '家有煮妇', '美式家',
           'office病患者', '雅致居家控', '木作匠人', '智慧家', 'SVIP壕', '中式贵族', '趣玩先锋', 'DIY达人', '赖床专业户', '轻微萌物癖', '钟情北欧风', '茶道中人',
           '厨艺达人', '新时代主妇', '囤货小当家', '租房一族', '装修家', '理想家'],
    "型男": ['大码界男神', '怕冷星人', '就是卫衣控', '请嫁给我吧', '不撞衫星人', '华尔街精英', '原宿少年', '摇滚朋克风', '中国有国潮', '轻奢一族', '高富帅', '潮鞋宠儿', '国风男子',
           '英伦也很帅', '硬汉', '军旅风', '机车骑士', '欧美型男', '追星族', '超级大学生', '牛仔很潮', '就爱大叔范', '格子控', '韩范', '欧巴', '手表控', 'SVIP壕',
           '非黑即白', '条纹控', '华丽上班族', '潮男俱乐部', '嘻哈一族', '码农style', '这小子真帅', '清新暖男', '男神style'],
    "园艺": ['绿植控', '多肉控'],
    "其他": [],
    "动漫": ['漫画迷', '二次元达人', 'COS巨巨'],
    "运动": ['棒球小子', '轮滑社', '足球爱好者', '滑雪族', '爱上高尔夫', '滑板少年', '网球小子', '极限挑战控', '灵魂冲浪手', '乒乓小将', '天文爱好者', '羽球小子', '极限飞盘社',
           '骑行控', '毛驴党', '登山爱好者', '钓鱼翁', '酷跑一族', '想要瘦瘦瘦', '瑜伽修炼者', '健身狂人', '水中飞鱼', '户外运动控'],
    "萌宠": ['喵星人', '汪星人', '萌宠大作战'],
    "美食": ['奶茶妹妹', '痛经忍者', '小小钢琴家', '家有双胞胎', '小小贵族范', '单身汪汪汪', '小小赛车手', '亲子合家欢', '小小画家', '芝士脑残粉', '迷恋迪士尼', '咖啡控',
           '轻食主义', '宝宝营养师', '小正太火锅', '爱好者', '吃不胖星人', '家有小学生', '好孕妈咪帮', '就爱吃点酸', '品酒大师', '无辣不欢者', '拼命十三郎', '肉食者阵地',
           '我是美食家', '我要当学霸', '就爱吃甜食', '水果大咖', '想要瘦瘦瘦', '养生达人', '重口味星人', '茶道中人', '早餐君', '吃货的后裔'],
    "美搭": ['我就是大怕冷星人', '就是卫衣控', '太平公主', '好想谈恋爱', '豹纹女王', '请嫁给我吧', '洛丽塔少女', '粉红少女心', '撞色控', '职场辣妈', '波点控', '轻奢一族',
           '性感尤物', '追星族', '流苏控', '文艺青年', '日系软妹', '港风男女', '旗袍女子', '清新森女', 'ulzzang风', '超级大学生', '极简主义', 'Bling控',
           'chic少女', '白富美', '职场白骨精', '美帽的你', '嘻哈一族', '街头少女', '裙控MM', '格子控', 'SVIP壕', '民族风帅气', 'BF风', '就爱设计感', '绝饰佳人',
           '华丽上班族', '制服党', '非黑即白', '蕾丝控', '条纹控', '欧美范儿', '清纯学院风', '复古女郎', '包治百病', '时髦小妖精', '美鞋控', '就爱宽松感', '气质名媛',
           'ins达人', '豆蔻少女', '女神范'],
    "游戏": ['游戏外设迷'],
    "数码科技": ['电脑发烧友', '耳机发烧友', '码农style', '炫酷极客控', '手机重患者'],
    "文化娱乐": ['中医世家', '哲学家', '吉他控', '历史狂享家', '挥毫泼墨派', 'Party党', '手工匠人', '绘画一族', '文玩控', '意气书生', '棋牌社', '就是爱乐人'],
    "美妆个护": ['大脸星人', '就爱限量版', '欧美妆容控', '口红控', '月球代言人', '爱国主义', '素颜女神', '油皮星人', '敏感的我', '日系美妆控', 'VIP壕', '干皮星人', '美发达人',
             '晚睡强迫症', '美妆达人']
}


def login():
    chrome_options = webdriver.ChromeOptions
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome()
    driver.get('https://drbl.daorc.com/login_login.action')
    driver.find_element_by_id('username').send_keys('7777754321')
    driver.find_element_by_id('password').send_keys('7777754321')
    driver.find_element_by_xpath('//*[@id="body"]/div/main/section/div[3]/div/div[1]/form/div[4]/div/button').click()
    cookies = driver.get_cookies()
    print(cookies)

    # header = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36",
    # }
    # url = "https://drbl.daorc.com/login_login.action"
    # response = requests.get(url, headers=header).text
    # token = re.findall('"token":[^}]*}', response)[0][9:-2]
    # print(token)
    #
    # url = 'https://drbl.daorc.com/user_jsonLogin.action'
    # data = {"loginName": "7777754321",
    #         "password": "7777754321",
    #         "checkyzm": '0',
    #         "struts.token.name": "token",
    #         "token": token}
    #
    # response = requests.post(url, data, verify=False).text
    #
    jsessionid = cookies[0]['value']
    HEADER['Cookie'] = "JSESSIONID=" + jsessionid
    driver.close()
    print('登录成功')


def get_response(page):
    """
    获取文章列表返回信息
    :param page:
    :return:
    """
    url = f"https://drbl.daorc.com/data_queryDataListToJSON.action?fileTypeId=99&tableFlag=WJ&t_fileTypeId=&t_tableFlag=&pageInfo=STATUS@@1@@2@_@AUTOSTATUS@@2@@2@_@STATUS@@1@@2@_@applications@@1524367772261@@2@_@&wherePageInfo=&ajPageInfo=&param_add_columns=&offset=20&limit=20&sort=&order=asc&page={page}&rows=100"
    while True:
        response = requests.get(url, headers=HEADER, verify=False).text
        try:
            info = json.loads(response)
            return info['rows']
        except:
            print('重新登录')
            login()
            continue


def insert_info(essay, cur):
    """
    解析文章信息并入库
    :param essay:
    :param cur:
    :return:
    """
    CHANNEL_CLASSIFICATION = essay['CHANNELID']
    CHANNEL_CLASSIFICATION_ID = essay['CHANNELID_1']
    try:
        CLASSIFICATION = essay['CLASSIFYID']
    except KeyError:
        CLASSIFICATION = ''
    try:
        CLASSIFICATION_ID = essay['CLASSIFYID_1']
    except KeyError:
        CLASSIFICATION_ID = -1
    ESSAY_CLASSIFICATION = essay['FILETYPEID']
    try:
        ESSAY_CLASSIFICATION_ID = essay['CLASSIFYID_1']
    except KeyError:
        ESSAY_CLASSIFICATION_ID = -1
    TITLE = essay['TITLE']
    # print(TITLE)
    ESSAY_ID = essay['ID']
    try:
        COVER_PICTURE_URL = json.loads(essay['COVERIMG'])[0]['coverUrl']
    except KeyError:
        COVER_PICTURE_URL = json.loads(essay['COVERIMG'])[0]['url']
    try:
        SUBMIT_ACOUNT = essay['SENDUSERINFONAME']
    except KeyError:
        SUBMIT_ACOUNT = ''
    CREATOR = essay['RESOURCEUSER']
    try:
        CREATOR_ID = essay['RESOURCEUSER_1']
    except KeyError:
        CREATOR_ID = ''
    CREATE_DATE = essay['CREATEDATE']
    STATUS = essay['AUTOSTATUS']
    try:
        STATUS_ID = essay['AUTOSTATUS_1']
    except KeyError:
        STATUS_ID = -1
    # sql = f'insert into essay_list(CHANNEL_CLASSIFICATION,CHANNEL_CLASSIFICATION_ID,CLASSIFICATION,CLASSIFICATION_ID,ESSAY_CLASSIFICATION,ESSAY_CLASSIFICATION_ID,COVER_PICTURE_URL,TITLE,ESSAY_ID,SUBMIT_ACOUNT,CREATOR,CREATOR_ID,CREATE_DATE,STATUS,STATUS_ID) ' \
    #       f'values ("{CHANNEL_CLASSIFICATION}",{CHANNEL_CLASSIFICATION_ID},"{CLASSIFICATION}",{CLASSIFICATION_ID},"{ESSAY_CLASSIFICATION}",{ESSAY_CLASSIFICATION_ID},"{COVER_PICTURE_URL}","{TITLE}","{ESSAY_ID}","{SUBMIT_ACOUNT}","{CREATOR}","{CREATOR_ID}","{CREATE_DATE}","{STATUS}",{STATUS_ID});'
    # num = cur.execute(sql)
    # print(f"插入了{num}条")
    print(TITLE, ESSAY_ID)


def get_fans_hotpoint_essay_list():
    """
    获取淘宝创意中心的粉丝热点文章
    :return:
    """
    conn = connect1_sql()
    cur = conn.cursor()
    for type in TYPES.keys():
        for i in range(1, 21):
            url = 'https://drbl.daorc.com/tbcreative_getCrowReWenData.action'
            data = {'area_tab_name': type, 'current_page': f'{i}'}
            response = requests.post(url, headers=HEADER, data=data, verify=False).text
            info_list = re.findall(r'\{[^<>]*\}', json.loads(response)['rewendata_html'])
            sql_list = []
            for info in info_list:
                info_dict = json.loads(info)
                print('图片链接：', info_dict['img'])
                print('热度：', info_dict['hotNum'])
                print('文章链接：', info_dict['link'])
                essay_id = info_dict['link'].split('contentId=')[1]
                print('文章编号', essay_id)
                print('内容分数：', info_dict['contentScore'])
                print('标题：', info_dict['title'].replace("'", '').replace('"', ''))
                print('文章类型：', info_dict['type'])
                sql = f"select count(*) from top_essay_list where ESSAY_ID={essay_id};"
                cur.execute(sql)
                num = cur.fetchone()[0]
                if num:
                    continue
                else:
                    sql = f"insert into top_essay_list (TITLE,ESSAY_ID,ESSAY_LINK,`TYPE`,FIELD,IMG_LINK) values('{info_dict['title']}',{essay_id},'{info_dict['link']}','{info_dict['type']}','{type}','{info_dict['img']}');"
                    print(sql)
                    cur.execute(sql)
            conn.commit()


url = 'https://down.daorc.com/main_welcome2.action?set=getContentReason'


def ele_in_str(string):
    expect_word = [
        '2015', '2016', '2017', '2018', '2014', '优惠', '涨价', '促销', '新款', '第二件', '全场', '购买', '包邮',
        '特惠 ', '折', '直供', '热卖', '爆款', '上新', '抢', '折扣', '打折', '毛泽东', '邓小平', '习近平', 'com', 'cn', 'net',
        '原价', '拍下', '限购', '特价', '元', '限时', "邮政", "顺丰", "圆通", "中通", "菜鸟驿站", "EMS", "ems", "德邦快递",
        "申通", "下单", "购买", "编辑部", "一二三四",
    ]
    for each in expect_word:
        if each in string:
            return True
    return False


def crawl_text(word):
    data = {
        "contentKeyWords": word
    }

    while True:
        try:
            response = requests.post(url, data=data, headers=HEADER, verify=False)
            break
        except:
            print("\033[31;1m由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。\033[0m")
            time.sleep(10)
    result_json = response.text
    try:
        result_python = json.loads(result_json)
    except json.decoder.JSONDecodeError:
        print(result_json)
        sys.exit()
    result_info = result_python['data']
    result_list = []
    unexcept_result_list = []
    for result in result_info:
        if '【' in result['summary'] or '分享自' in result['summary'] or ele_in_str(result['summary']) or not much_blank(
                result['summary']):
            continue
        elif 20 > len(result['summary']):
            unexcept_result_list.append(result['summary'].replace('<br>', ''))
        else:
            result_list.append(result['summary'].replace('<br>', ''))
    return result_list, unexcept_result_list


def crawl_badou_top_essay_list():
    login()
    get_fans_hotpoint_essay_list()


def crawl_badou_essay_list():
    login()
    page = 0
    conn = connect1_sql()
    cur = conn.cursor()
    while True:
        page += 1
        essay_list = get_response(page)
        j = 0
        for essay in essay_list:
            j += 1
            print('页码：', page, f'第{j}条')
            insert_info(essay, cur)
        conn.commit()


def much_blank(string):
    count = 0
    for w in string:
        if w == " ":
            count += 1
        if count > 2:
            return False
    else:
        return True


def get_text(name, sc):
    conn1 = connect_mysql.w_shark_erp()
    cur1 = conn1.cursor()
    conn2 = connect_mysql.w_shark_erp()
    cur2 = conn2.cursor()
    while True:
        try:
            info = sc.pop()
        except IndexError:
            cur1.close()
            conn1.close()
            cur2.close()
            conn2.close()
            break
        result_list, unexcept_result_list = crawl_text(info[1])
        # if len(result_list) < 3 and len(unexcept_result_list) < 3:
        #     print(info[1], '暂无文案')
        #     sql = f"""update cm_commodity  set HAVE_TEXT=3 WHERE URL_ID='{info[0]}';"""
        #     cur1.execute(sql)
        #     conn1.commit()
        #     continue

        sql = f"""insert into crawler_commodity_module_description_copy (CONTENT,URL_ID) VALUES ("{str(result_list).replace('"', ",")}","{info[0]}" );"""

        conn2.ping(True)
        while True:
            try:
                cur2.execute(sql)
                break
            except pymysql.err.OperationalError:
                cur2.close()
                conn2.close()
                conn2 = connect_mysql.local_bs()
                cur2 = conn2.cursor()
        conn2.commit()


        print(name, datetime.datetime.now(), info[1])


def get_DIY_essays():
    login()
    page = 0
    conn = connect_mysql.test()
    cur = conn.cursor()
    sql = """insert into erp_original_essay(ESSAY_ID,TEXT) values (%s,%s);"""
    while True:
        page += 1
        url = f"https://drbl.daorc.com/data_queryDataListToJSON.action?fileTypeId=99&tableFlag=WJ&pageInfo=STATUS@@1@@2@_@AUTOSTATUS@@1,2,3,4,5,6,7,8,9,10@@7@_@STATUS@@1@@2@_@applications@@1524367772261@@2@_@&limit=100&page={page}"
        response = requests.get(url, headers=HEADER).text
        result = json.loads(response)
        for each in result['rows']:
            id = each['ID']
            channelid_1 = each['CHANNELID_1']

            if channelid_1 in ['7714', '1661']:  # 单品
                essay_url = f"https://drbl.daorc.com/tbimagetxtcard_messageCheckView.action?id={id}&fileTypeId=7714&temp={time.time()}"
                response = requests.get(essay_url, headers=HEADER).text
                f_text_list = re.findall("""<div style='margin-top: 15px'>[^(</div>)]*</div>""", response)
                text_list = []
                for f_text in f_text_list:
                    text = f_text.split('>', 1)[1][:-6]
                    text_list.append((id, text.replace('"', "'").replace("\n", "")))
                    print(datetime.datetime.now(), text)

            elif channelid_1 == "1507":  # 图文帖子
                essay_url = f"https://drbl.daorc.com/data_updateData.action?tableFlag=WJ&id={id}&fileTypeId={channelid_1}&temp={time.time()}"
                response = requests.get(essay_url, headers=HEADER).text
                f_text_list = re.findall("""&lt;p&gt;[^&]*&lt;/p&gt;""", response)
                text_list = []
                for f_text in f_text_list:
                    text = f_text.strip("&lt;p&gt;").strip("&lt;/p&gt;")
                    text_list.append((id, text.replace('"', "'").replace("\n", "")))
                    print(datetime.datetime.now(), text)

            elif channelid_1 in ["1656", "1649", "102"]:  # 搭配
                essay_url = f"https://drbl.daorc.com/data_updateData.action?id={id}&tableFlag=WJ&fileTypeId={channelid_1}&temp={time.time()}"
                response = requests.get(essay_url, headers=HEADER).text
                f_text_list = re.findall("""name='RECOREASON' inputType='1' >[^<>]*<""", response)
                text_list = []
                for f_text in f_text_list:
                    text = f_text.strip("name='RECOREASON' inputType='1' >").strip("<")
                    text_list.append((id, text.replace('"', "'").replace("\n", "")))
                    print(datetime.datetime.now(), text)
            elif channelid_1 in ["1659"]:  # 清单
                essay_url = f"https://drbl.daorc.com/data_updateData.action?id={id}&tableFlag=WJ&fileTypeId={channelid_1}&temp={time.time()}"
                response = requests.get(essay_url, headers=HEADER).text
                f_text_list = re.findall("""name='REMARK' inputType='1' >[^<>]*<""", response)
                text_list = []
                for f_text in f_text_list:
                    text = f_text.strip("name='REMARK' inputType='1' >").strip("<")
                    text_list.append((id, text.replace('"', "'").replace("\n", "")))
                    print(datetime.datetime.now(), text)
            else:
                text_list = []
                continue
            cur.executemany(sql, text_list)
            conn.commit()
        if len(result['rows']) < 100:
            break


def daemon():
    while True:
        try:
            urllib3.disable_warnings()
            global HEADER
            HEADER = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            login()
            sql = """select distinct(URL_ID),TITLE,ID,CREATE_DATE from cm_commodity where CREATE_DATE > "2019-11-14 " and URL_ID NOT IN(SELECT URL_ID FROM crawler_commodity_module_description_copy) ORDER BY CREATE_DATE DESC limit 2000;"""
            Schedule = schedule.schedule(sql, connect_mysql.w_shark_erp())
            print('开始线程')
            t1 = mythread("1", Schedule, )
            # t2 = mythread("2", Schedule, )
            # t3 = mythread("3", Schedule, )
            # t4 = mythread("4", Schedule, )
            # t5 = mythread("5", Schedule, )
            # t6 = mythread("6", Schedule, )
            # t7 = mythread("7", Schedule, )
            # t8 = mythread("8", Schedule, )
            # t9 = mythread("9", Schedule, )
            # t10 = mythread("0", Schedule, )

            t1.start()
            print('线程1启动')
            time.sleep(1)

            # t2.start()
            # print('线程2启动')
            # time.sleep(1)
            #
            # t3.start()
            # print('线程3启动')
            # time.sleep(1)
            #
            # t4.start()
            # print('线程4启动')
            # time.sleep(1)
            #
            # t5.start()
            # print('线程5启动')
            # time.sleep(1)
            #
            # t6.start()
            # print('线程6启动')
            # time.sleep(1)
            #
            # t7.start()
            # print('线程7启动')
            # time.sleep(1)
            #
            # t8.start()
            # print('线程8启动')
            # time.sleep(1)
            #
            # t9.start()
            # print('线程9启动')
            # time.sleep(1)
            #
            # t10.start()
            # print('线程10启动')
            # time.sleep(1)

            # t10.join()
            # t9.join()
            # t8.join()
            # t7.join()
            # t6.join()
            # t5.join()
            # t4.join()
            # t3.join()
            # t2.join()
            t1.join()
        except:
            pass


if __name__ == '__main__':
    # conn = connect_mysql.test()
    # cur = conn.cursor()
    # sql = """select distinct(ESSAY_ID) from erp_original_essay;"""
    # cur.execute(sql)
    # essayid_list = []
    # for each in cur.fetchall():
    #     essayid_list.append(each[0])
    # HEADER = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36',
    #     'Cookie': None
    # }
    # get_DIY_essays()

    daemon()
