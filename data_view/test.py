import connect_mysql
import time
import hashlib
from urllib import parse
import requests
import re
import json
import traceback
import random

import numpy as np

import tb_toutiao

tt = tb_toutiao.touTiao()
sql = "select ID,TITLE from tb_toutiao where CLASSIFY is null;"
tt.cur_T.execute(sql)
for item in tt.cur_T.fetchall():
    classify = tt.findClass(item[1])
    print(item, classify)
    sql = "update tb_toutiao set CLASSIFY=%s where ID=%s;"
    tt.conn_T.ping(True)
    tt.cur_T.execute(sql, [classify, item[0]])
    tt.conn_T.commit()
tt.closeSql_T()
tt.closeSql_W()
