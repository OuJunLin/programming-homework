import datetime
import mysql.connector as myconn
import hashlib

def getTime():
    time1 = datetime.datetime.now()
    time_now = time1.strftime("%Y/%D")
    time_now = time_now[:len(time_now)-3] + time1.strftime(" %H.%M.%S")
    return time_now

dbConn = myconn.connect(
    host = "localhost",
    user = "root",
    password = "super007oj87",
    database = "server_database"
)
cursor = dbConn.cursor()

def hash256Encode(n:str):
    m = hashlib.sha256()
    m.update(n.encode("utf-8"))
    return m.hexdigest()



def insertToTable_AccountPassword(account:str, password:str):
    pw = password
    pw = hash256Encode(pw)
    cursor.execute('INSERT INTO `account_password`(account, password) VALUES ("{}", "{}")' .format(account, pw))
    dbConn.commit()



def get_account_password():
    password_dict = {}
    cursor.execute("SELECT * FROM `account_password`;")
    result1 = cursor.fetchall()
    for row in result1:
        password_dict[row[1]] = row[2]
    return password_dict







