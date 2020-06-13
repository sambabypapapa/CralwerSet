import CralwerSet.connect_mysql as connect_mysql
import time
import json

classify = 2
info = '付製这行话￥daxi1oVNWaF￥转移至淘宀┡ē【不会自行车的我，不想买贵的大的电动车，怕学不会，就入手了希洛普的电动滑板车，车子价位从1K多起步】；或https://m.tb.cn/h.VjtdO5K?sm=4d4548 點击链街，再选择瀏..覽..噐dakai'
temp = str(int(time.time() * 1000))
r = connect_mysql.Redis()
key = temp + '|' + str(classify) + '|' + info
r.hset('wt', key, '')
info = {}
while True:
    time.sleep(0.1)
    result = r.hget("wt", key).decode('utf-8')
    if not result:
        continue
    info = json.loads(result)
    r.hdel('wt', key)
    break
if type(info['urlList']) == list:
    print(info['urlList'])
    print(info['text'])
else:
    if int(info['urlList']) == 401:
        print('链接解析错误')
    elif int(info['urlList']) == 402:
        print('页面请求失败')
