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



def insert_to_account_password(account:str, password:str):
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



def insert_to_user_data(account:str, sorce:int, grade:int):
    cursor.execute('INSERT INTO `user_data`(account, sorce, grade) VALUES ("{}", {}, {})' .format(account, sorce, grade))
    dbConn.commit()



def get_user_data():
    user_data_list = {}
    cursor.execute("SELECT * FROM `user_data`;")
    for row in cursor.fetchall():
        user_data_list[row[1]] = [row[2], row[3]]

    return user_data_list



def insert_to_img_info(class_:str, file_name:str,time_, nick_name:str):
    now_time = getTime()
    cursor.execute('INSERT INTO `img_info`(class, file_name, time, Nick_name) VALUES ("{}", "{}", "{}", "{}")' .format(class_, file_name, time_, nick_name))
    dbConn.commit()



def get_img_info():
    img_data_dict = {}
    cursor.execute("SELECT * FROM `img_info`;")
    for row in cursor.fetchall():
        img_data_dict[row[4]] = [row[1], row[2], row[3]]
    return img_data_dict



def update_img_info_Nick_name(new_name:str, old_name:str):
    check = get_img_info()
    if old_name in check:
        cursor.execute('UPDATE `img_info` SET Nick_name = "{}" WHERE Nick_name = "{}";' .format(new_name, old_name))
        dbConn.commit()
    else:
        print("not in db")



def delete_img_info(name:str):
    cursor.execute('DELETE FROM `img_info` WHERE Nick_name = "{}";' .format(name))
    dbConn.commit()



def inser_to_chatroom_record(account:str, msg:str):
    nowtime = getTime()
    cursor.execute('INSERT INTO `chatroom_record`(account, msg, time) VALUES ("{}", "{}", "{}")' .format(account, msg, nowtime))
    dbConn.commit()



def insert_to_phone_record(phone:str):
    cursor.execute('INSERT INTO `phone_record`(phone, time) VALUES ("{}", "{}")' .format(phone, getTime()))
    dbConn.commit()



def update_account_password(newpassword:str, account:str):
    cursor.execute('UPDATE `account_password` SET password = "{}" WHERE account = "{}"'.format(newpassword, account))
    dbConn.commit()



def update_user_data(set_choose:str, set_content:str, user_name:str):
    cursor.execute('UPDATE `user_data` SET {} = "{}" WHERE account = "{}"'.format(set_choose, set_content, user_name))
    dbConn.commit()



def delete_user_data_account(account:str):
    cursor.execute('DELETE FROM `user_data` WHERE account = "{}";' .format(account))
    dbConn.commit()



def delete_account_password_account(account:str):
    cursor.execute('DELETE FROM `account_password` WHERE account = "{}";' .format(account))
    dbConn.commit()













