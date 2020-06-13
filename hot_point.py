import requests
import CralwerSet.connect_mysql as connect_mysql
import time
import json
import datetime
import threading
from requests.packages import urllib3
import re
import urllib.parse
from bs4 import BeautifulSoup
import traceback


def xiaoHongShu():
    pass


def douYin():
    threading.Thread(target=douYinHotPoint).start()
    threading.Thread(target=douYinVideo).start()
    threading.Thread(target=douYinPositiveEnergy).start()
    time.sleep(20)
    while True:
        time.sleep(600)


def douYinHotPoint():
    try:
        while True:
            # 抖音热点榜
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}
            conn = connect_mysql.test()
            cur = conn.cursor()
            while True:
                response = requests.get(url=url, headers=headers, verify=False).text
                result = json.loads(response)
                word_list = []
                for each in result['word_list']:
                    word = {
                        'desc': each['word'],
                        'desc_extr': each['hot_value'],
                        "url": f"""https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={urllib.parse.quote(each['word'].replace('"', ""))}"""
                    }
                    word_list.append(word)

                sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(word_list, ensure_ascii=False)}',updatetime=now() where `FROM`='热点榜'; """
                conn.ping(True)
                cur.execute(sql)
                conn.commit()
                time.sleep(600)
    except:
        traceback.print_exc()
        cur.close()
        conn.close()


def douYinVideo():
    try:
        while True:
            # 抖音视频榜
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/aweme/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}
            conn = connect_mysql.test()
            cur = conn.cursor()
            while True:
                response = requests.get(url=url, headers=headers, verify=False).text
                result = json.loads(response)
                word_list = []
                for each in result['aweme_list']:
                    word = {
                        'desc': each['aweme_info']['desc'],
                        'desc_extr': each['label'],
                        "url": f"""https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={urllib.parse.quote(each['aweme_info']['desc'].replace('"', ""))}"""
                    }
                    word_list.append(word)
                sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(word_list, ensure_ascii=False)}', updatetime=now() where `FROM`='视频榜'; """
                cur.execute(sql)
                conn.commit()
                time.sleep(86400)
    except:
        traceback.print_exc()
        cur.close()
        conn.close()

def douYinPositiveEnergy():
    try:
        while True:
            # 抖音正能量
            conn = connect_mysql.test()
            cur = conn.cursor()
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/aweme/?type=positive"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}
            response = requests.get(url=url, headers=headers, verify=False).text
            result = json.loads(response)
            while True:

                word_list = []
                for each in result['aweme_list']:
                    word = {
                        'desc': each['aweme_info']['desc'].replace('"', ""),
                        'desc_extr': each['hot_value'],
                        "url": f"""https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&word={urllib.parse.quote(each['aweme_info']['desc'].replace('"', ""))}"""
                    }
                    word_list.append(word)

                sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(word_list, ensure_ascii=False)}', updatetime=now() where `FROM`='正能量'; """
                cur.execute(sql)
                conn.commit()
                time.sleep(86400)
    except:
        traceback.print_exc()
        cur.close()
        conn.close()


def weiBo():
    hotSearch_url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot&title=%E5%BE%AE%E5%8D%9A%E7%83%AD%E6%90%9C&extparam=pos%3D0_0%26mi_cid%3D100103%26cate%3D10103%26filter_type%3Drealtimehot%26c_type%3D30%26display_time%3D1572329575&luicode=10000011&lfid=231583"
    movie_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_100_-_%E7%94%B5%E5%BD%B1%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08 "
    ssMeizhuag_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_114_-_%E6%97%B6%E5%B0%9A%E7%BE%8E%E5%A6%86%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    travel_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_93_-_%E6%97%85%E6%B8%B8%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    foods_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_91_-_%E7%BE%8E%E9%A3%9F%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    picture_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_123_-_%E7%BE%8E%E5%9B%BE%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    car_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_117_-_%E6%B1%BD%E8%BD%A6%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    cat_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_128_-_%E8%90%8C%E5%AE%A0%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    child_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_116_-_%E8%82%B2%E5%84%BF%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    digital_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_131_-_%E6%95%B0%E7%A0%81%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    home_url = "https://m.weibo.cn/api/container/getIndex?containerid=231648_-_1_-_504_hot_-_%E5%AE%B6%E5%B1%85%E8%AF%9D%E9%A2%98%E6%A6%9C_-_2&luicode=10000011&lfid=231648_-_7_-_2&page_type=08"
    topic_url_list = [movie_url, ssMeizhuag_url, travel_url, foods_url, picture_url, car_url, cat_url, child_url,
                      digital_url, home_url]
    try:
        while True:
            conn = connect_mysql.test()
            cur = conn.cursor()
            hotSearch_time = 0
            topic_time = 0

            while True:
                # 微博热搜
                # 一分钟更新一次
                topic_dict = {'电影话题榜': '电影话题榜',
                              '时尚美妆话题榜': '时尚美妆话题榜',
                              '旅游话题榜': '旅游话题榜',
                              '美食话题榜': '美食话题榜',
                              '美图话题榜': '美图话题榜',
                              '汽车话题榜': '汽车话题榜',
                              '萌宠话题榜': '萌宠话题榜',
                              '育儿话题榜': '育儿话题榜',
                              '数码话题榜': '数码话题榜',
                              '家居话题榜': '家居话题榜'
                              }
                if time.time() - hotSearch_time > 60:
                    hotSearch_time = time.time()
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}
                    hotSearch_response = requests.get(url=hotSearch_url, headers=headers, verify=False).text
                    try:
                        hotSearch_result = json.loads(hotSearch_response)
                    except:
                        traceback.print_exc()
                        continue
                    card_group = hotSearch_result['data']['cards'][0]['card_group']
                    card_list = []
                    for card in card_group[1:]:
                        card_list.append({'desc': card['desc'], 'desc_extr': card['desc_extr'], "url": card["scheme"]})
                    sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(card_list, ensure_ascii=False)}', updatetime=now() where `FROM`='热搜榜'; """
                    conn.ping(True)
                    cur.execute(sql)
                    conn.commit()
                    card_group = hotSearch_result['data']['cards'][1]['card_group']
                    card_list = []
                    for card in card_group:
                        card_list.append({'desc': card['desc'], 'desc_extr': card['desc_extr'], "url": card["scheme"]})
                    sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(card_list, ensure_ascii=False)}',updatetime=now() where `FROM`='实时上升热点'; """
                    cur.execute(sql)
                    conn.commit()

                # 微博实时上升热点
                # 一天更新一次
                if time.time() - topic_time > 86400:
                    topic_time = time.time()
                    # 获取电影话题排行榜
                    headers['Cache-Control'] = "max-age=0"
                    headers[
                        'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
                    headers['Upgrade-Insecure-Requests'] = '1'
                    headers['Connection'] = 'keep-alive'
                    headers[
                        'Cookie'] = "_T_WM=69451734627; MLOGIN=0; WEIBOCN_FROM=1110003030; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D231648_-_7_-_2%26fid%3D231648_-_1_-_504_hot_-_%25E5%25AE%25B6%25E5%25B1%2585%25E8%25AF%259D%25E9%25A2%2598%25E6%25A6%259C_-_2%26uicode%3D10000011; XSRF-TOKEN=94520d"
                    for url in topic_url_list:
                        topic_class_temp = re.findall('_%[^_]*%9C_', url)[0]
                        topic_class = urllib.parse.unquote(topic_class_temp.strip('_').replace('"', "'"))
                        card_list = weiBo_topic(url, headers)
                        sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(card_list, ensure_ascii=False)}',updatetime=now() where `FROM`="{topic_dict[topic_class]}"; """
                        cur.execute(sql)
                        conn.commit()
    except:
        traceback.print_exc()
        cur.close()
        conn.close()


def weiBo_topic(first_url, headers):
    # 只能用于爬取微博话题
    page = 1
    card_list = []
    while True:
        movie_response = requests.get(url=first_url + f"&page={page}", headers=headers, verify=False)

        page += 1
        movie_response_text = movie_response.text
        try:
            movie_result = json.loads(movie_response_text)
        except:

            traceback.print_exc()
        # 未获取到内容时退出循环
        try:
            card_group = movie_result['data']['cards'][0]['card_group']
        except IndexError:
            break

        except KeyError:
            break

        for card in card_group:
            card_list.append({'desc': card['title_sub'], 'desc_extr': card['desc2'], 'url': card['scheme']})
    return card_list


def baiDu():
    try:
        while True:
            # 实时热点
            rt_url = "http://top.baidu.com/buzz?b=1&c=513&fr=topbuzz_b341_c513"
            # 今日热点
            td_url = "http://top.baidu.com/buzz?b=341&c=513&fr=topbuzz_b1_c513"
            # 七日热点
            sd_url = "http://top.baidu.com/buzz?b=42&c=513&fr=topbuzz_b341_c513"
            conn = connect_mysql.test()
            cur = conn.cursor()
            hotPoint_dict = {
                '实时热点': rt_url,
                '今日热点': td_url,
                '七日热点': sd_url
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36'}

            while True:
                for each in hotPoint_dict.keys():
                    response = requests.get(url=hotPoint_dict[each], headers=headers, verify=False).content.decode('gbk')
                    soup = BeautifulSoup(response, "html.parser")
                    table = soup.find('table', {'class': 'list-table'})
                    tr_list = table.find_all('tr')[1:]
                    card_list = []
                    for tr in tr_list:
                        try:
                            titlt = tr.find('a', {'class': 'list-title'}).text.strip("\n")
                            url = tr.find('a', {'class': 'list-title'})['href']
                        except AttributeError:
                            continue
                        try:
                            value = tr.find('span', {'class': 'icon-fall'}).text.strip("\n")
                        except AttributeError:
                            try:
                                value = tr.find('span', {'class': 'icon-rise'}).text.strip("\n")
                            except AttributeError:
                                value = tr.find('span', {'class': 'icon-fair'}).text.strip("\n")
                        card_list.append({'desc': titlt, 'desc_extr': value, 'url': url})
                    sql = f"""update erp_hotpoint set HOTPOINT='{json.dumps(card_list, ensure_ascii=False)}',updatetime=now() where `FROM`="{each}"; """
                    cur.execute(sql)
                    conn.commit()
                time.sleep(120)
    except:
        traceback.print_exc()
        cur.close()
        conn.close()


def touTiao():
    pass

if __name__ == '__main__':
    urllib3.disable_warnings()
    threading.Thread(target=weiBo).start()
    threading.Thread(target=baiDu).start()
    threading.Thread(target=douYin).start()
