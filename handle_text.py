import CralwerSet.connect_mysql as connect_mysql
import json
import Levenshtein
import datetime
import pymysql


def diff(string, List):
    for each in List:
        if Levenshtein.ratio(string, each) > 0.8:
            return False
    return True

conn = connect_mysql.w_shark_erp()
cur = conn.cursor()
insertSql = "insert into cm_text(TEXT) values (%s);"

with open("split_text_record.json", 'r') as f:
    load_dict = json.load(f)
tooLongText = []
for id in range(load_dict['started'],823550,100):
    allText = []
    sql = f"select * from crawler_commodity_module_description where ID>={id} and ID < {id + 100};"
    cur.execute(sql)
    result = cur.fetchall()
    for each in result:
        textSplitList = each[2][2:-2].split("', '")
        unitTextList = []
        while textSplitList:
            text = textSplitList.pop()
            if diff(text, textSplitList) :
                unitTextList.append(text)
        allText += unitTextList

    cur.executemany(insertSql, allText)
    conn.commit()


    with open("split_text_record.json", 'w') as f:
        f.write('{"started": '+ str(id + 100) +'}')
    print(datetime.datetime.now(), id)
with open("tooLongText.txt",'a') as f:
    f.write(str(tooLongText))
cur.close()
conn.close()