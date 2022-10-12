import core

db_operator = core.DataBaseOperator()

db_operator.cur.execute('select method_time,method_name from notes')
datas = db_operator.cur.fetchall()

for i in range(len(datas)):
    datas[i] = (i,datas[i][0],datas[i][1])
    print(datas[i])

db_operator.cur.executemany('update notes set time=? where method_time=? and method_name=?',datas)

db_operator.close()