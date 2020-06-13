from XiaoHS import xhs_search as xs
import CralwerSet.connect_mysql as connect_mysql


r = connect_mysql.Redis()

xs.write_key(r)


# ConnectionHandler got an error : java.net.ConnectException: failed to connect to /192.168.1.102 (port 8888) after 30000ms: connect failed: ENETUNREACH (Network is unreachable)
# 手机淘宝<->203.119.144.34:443
# https://mapi.weibo.com/2/comments/build_comments?is_show_bulletin=2&c=android&s=04d3302c&id=4512909209737074
# https://mapi.weibo.com/2/comments/build_comments?is_show_bulletin=2&c=android&s=04d3302c&id=4513512946808683