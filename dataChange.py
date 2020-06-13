"""
将cm_text 文案转移到cm_text_new库中
"""

import CralwerSet.connect_mysql as connect_mysql
import traceback

conn = connect_mysql.w_shark_erp()
cur = conn.cursor()
try:
    for i in range(12950641, 53503537, 100000):
        print(i)
        sql = f"INSERT INTO cm_text_new(URL_ID,TEXT) SELECT IFNULL(URL_ID, 0),TEXT FROM cm_text WHERE ID>={i} and ID <{i + 100000};"
        conn.ping(True)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()
except:
    traceback.print_exc()
    cur.close()
    conn.close()
