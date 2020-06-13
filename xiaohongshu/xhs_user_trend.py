import CralwerSet.connect_mysql as connect_mysql

def main():
    conn = connect_mysql.test()
    cur = conn.cursor()
    sql = "select DISTINCT USER_KEY from xhs_attention_user where FANS_UP_RAT=1;"

    cur.execute(sql)

    for user_key in [item[0] for item in cur.fetchall()]:
        sql = f"select ID, USER_KEY,FANS,LIKED,COLLECT,NOTES from xhs_attention_user where USER_KEY={user_key} order by ID;"
        cur.execute(sql)
        result = cur.fetchall()
        data = []
        for i in range(len(result)):
            print(result[i][0], result[i][1])
            if i == 0:
                fans_up_num = 0
                liked_up_num = 0
                collect_up_num = 0
                notes_up_num = 0
                fans_up_rat = 0
                liked_up_rat = 0
                collect_up_rat = 0
                notes_up_rat = 0
            else:
                fans_up_num = result[i][2] - result[i - 1][2]
                liked_up_num = result[i][3] - result[i - 1][3]
                collect_up_num = result[i][4] - result[i - 1][4]
                notes_up_num = result[i][5] - result[i - 1][5]
                if result[i - 1][2]:
                    fans_up_rat = fans_up_num / result[i - 1][2] * 1000
                else:
                    fans_up_rat = 0
                if result[i - 1][3]:
                    liked_up_rat = liked_up_num / result[i - 1][3] * 1000
                else:
                    liked_up_rat = 0
                if result[i - 1][4]:
                    collect_up_rat = collect_up_num / result[i - 1][4] * 1000
                else:
                    collect_up_rat = 0
                if result[i - 1][5]:
                    notes_up_rat = notes_up_num / result[i - 1][5] * 1000
                else:
                    notes_up_rat = 0
            data.append(
                [fans_up_rat, liked_up_rat, collect_up_rat, notes_up_rat, fans_up_num, liked_up_num, collect_up_num,
                 notes_up_num, result[i][0]])
        sql = "update xhs_attention_user set FANS_UP_RAT=%s,LIKED_UP_RAT=%s,COLLECT_UP_RAT=%s,NOTES_UP_RAT=%s,FANS_UP_NUM=%s,LIKED_UP_NUM=%s,COLLECT_UP_NUM=%s,NOTES_UP_NUM=%s where ID=%s;"
        conn.ping(True)
        cur.executemany(sql, data)
        conn.commit()
    cur.close()
    conn.close()