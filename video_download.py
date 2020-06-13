import requests
import redis
import time


def getParse(url):
    endString = url.split('?', 1)[1]
    parse = {}
    for item in endString.split("&"):
        parse[item.split('=',1)[0]] = item.split('=',1)[1]
    return parse

def WeiboRequest(url):
    parse = getParse(url)
    id = parse['id']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3724.8 Safari/537.36",
        "Cookie": "SINAGLOBAL=9038348472751.512.1578984453578; UOR=m.weibo.cn,gouwu.sc.weibo.com,tech.ifeng.com; ALF=1594171025; SUB=_2A25z2eHBDeRhGedG41UT9C_JzT2IHXVRJY-JrDV8PUJbkNANLRjGkW1NUOsimoIvT4rAQ_nQ4DkOD61J5hFeiFpc; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFUOfMn2-VhNbl3gRQj_1JN5JpX5oz75NHD95Qp1hnNeoBpSKqpWs4Dqcj.i--ciKnRiK.pi--NiKnRi-zpi--Ni-i2iK.NxPyXMJH_9gp4; _s_tentry=-; Apache=2131449212986.5715.1591671522794; ULV=1591671522811:2:1:1:2131449212986.5715.1591671522794:1578984453594"
    }
    url = f"https://mapi.weibo.com/2/comments/build_comments?is_show_bulletin=2&c=android&s=04d3302c&id={id}"
    response = requests.get(url, headers=headers, verify=False)
    content = response.text
    return content





