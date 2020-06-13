import Levenshtein
import CralwerSet.connect_mysql as connect_mysql
import datetime
import copy
import traceback


def diff(string, List):
    for each in List:
        if Levenshtein.ratio(string, each[1]) > 0.8:
            return False
    return True


# conn = connect_mysql.w_shark_erp()
# cur = conn.cursor()
#
# del_sql = "delete from cm_text_new1 where ID in %s;"
#
# count_sql = "select `LONG`,COUNT(`LONG`) num from cm_text_new1 GROUP BY `LONG` ORDER BY num desc;"
# cur.execute(count_sql)
# for long, num in cur.fetchall():
#     page = 1
#     while num > 1:
#         print(page)
#         sql = f"select ID,TEXT from cm_text_new1 where `LONG`={long} limit {page},10000"
#
#         cur.execute(sql)
#         text_list = list(cur.fetchall())
#         check_num = len(text_list)
#         text_list1 = copy.deepcopy(text_list)
#         id_list = []
#         uniqe_id_list = []
#         for each in text_list:
#             for each1 in text_list1:
#                 if each[0] < each1[0]:
#                     if each[1][1] == each1[1][1] and each[1][-1] == each1[1][-1] and each[1] == each1[1] and each1[0] not in id_list:
#                         text_list.remove(each1)
#                         id_list.append(each1[0])
#                     else:
#                         continue
#         for item in text_list:
#             uniqe_id_list.append(item[0])
#
#         print('剩余文案数量',len(text_list),uniqe_id_list)
#         print('已排除文案数量',len(id_list),id_list)
#         print('总文案数',len(id_list) + len(text_list))
#         page += len(text_list)
#         conn.ping(True)
#         if len(id_list):
#             if len(id_list) == 1:
#                 cur.execute(del_sql % (f'({id_list[0]})'))
#             else:
#                 cur.execute(del_sql % (str(tuple(id_list))))
#             conn.commit()
#         if check_num < 10000:
#             break
#
# cur.close()
# conn.close()


conn = connect_mysql.w_shark_erp()
cur = conn.cursor()

del_sql = "delete from cm_text_new1 where ID in %s;"

page = 9035892

while True:
    print(page)
    sql = f"select ID, TEXT, `LONG` from cm_text_new1 where ID >={page} limit 1;"
    cur.execute(sql)
    page, text, long = cur.fetchone()
    sql = f"""select ID, TEXT, `LONG` from cm_text_new1 where `LONG`={long} and ID >={page} and match(TEXT) against('{text[:7].replace("'","")}') ORDER BY ID limit 10000;"""
    page += 1
    print(sql)
    cur.execute(sql)
    text_list = list(cur.fetchall())
    if not text_list:
        continue
    check_num = len(text_list)
    text_list1 = copy.deepcopy(text_list)
    id_list = []
    uniqe_id_list = []
    print('开始比较',datetime.datetime.now())
    for each in text_list:
        for each1 in text_list1:
            if each[0] < each1[0]:
                if each1[2] == each[2] and each[1][1] == each1[1][1] and each[1][-1] == each1[1][-1] and each[1] == each1[1] and each1[
                    0] not in id_list:
                    text_list.remove(each1)
                    id_list.append(each1[0])
                else:
                    continue
    print('结束比较', datetime.datetime.now())
    for item in text_list:
        uniqe_id_list.append(item[0])

    print('剩余文案数量', len(text_list))
    print('已排除文案数量', len(id_list))
    print('总文案数', len(id_list) + len(text_list))
    page += len(text_list)
    conn.ping(True)
    if len(id_list):
        if len(id_list) == 1:
            cur.execute(del_sql % (f'({id_list[0]})'))
        else:
            cur.execute(del_sql % (str(tuple(id_list))))
        conn.commit()
    if page > 48565432:
        break

cur.close()
conn.close()
