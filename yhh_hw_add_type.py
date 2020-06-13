"""
添加好物类别
"""
import CralwerSet.connect_mysql as connect_mysql
import traceback

conn_T = connect_mysql.test()
cur_T = conn_T.cursor()
conn_W = connect_mysql.w_shark_erp()
cur_W = conn_W.cursor()
sql = "select ID, TITLE from yhh_hw where ID>14000;"
cur_T.execute(sql)

try:
    for item in cur_T.fetchall():
        sql = f"""SELECT t6.cat,t5.num FROM (select t4.MAIN_ID MAIN_ID,count(t4.MAIN_ID) num FROM (SELECT  t2.CLASSIFY_ID CLASSIFY_ID FROM (select URL_ID, CONTENT from crawler_commodity_module_description where match(CONTENT) against('{item[1].replace("'","’")}') limit 100) t1, cm_commodity t2 where t1.URL_ID=t2.URL_ID ) t3, class_id t4 where t3.CLASSIFY_ID = t4.ID GROUP BY t4.MAIN_ID) t5, class_id t6 WHERE t6.ID=t5.MAIN_ID ORDER BY t5.num desc LIMIT 1;"""
        cur_W.execute(sql)
        result = cur_W.fetchone()
        if not result:
            type = '类型不明'
        else:
            type = result[0][:-1]
        sql = f"""update yhh_hw set `TYPE`='{type}' where ID={item[0]} limit 1;"""
        cur_T.execute(sql)
        conn_T.commit()
        print(item[0], item[1], type)
except:
    traceback.print_exc()
cur_T.close()
conn_T.close()
cur_W.close()
conn_W.close()