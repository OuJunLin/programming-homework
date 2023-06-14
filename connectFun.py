import socket
import threading
import mysql.connector as myconn
import datetime
import MySQLFun
import time
from os import listdir, remove
from os.path import isfile, isdir, join
from face_engine import load_engine

current_client_dict = {}
chatroom_client_dict = {}
ttt_wait_dict = {}


def get_current_clients():
    global current_client_dict
    return current_client_dict



def getFilePath(mypath):
    files = listdir(mypath) 
    file_list = []
    for f in files:
        fullpath = join(mypath, f)
        if isfile(fullpath):
            file_list.append(fullpath)
        elif isdir(fullpath):
            for f2 in getFilePath(fullpath):
                file_list.append(f2)
    return file_list



def send_img(connl, img_path):
    imgFile = open(img_path, "rb")
    while True:
        imgData = imgFile.readline(1024)
        connl.send(imgData)
        if not imgData:
            break  
    imgFile.close()
    time.sleep(0.1)
    connl.send("transmit end".encode())



def recv_img(connl, save_path):
    imgFile = open(save_path, 'wb')  
    while True:
        imgData = connl.recv(1024)
        if imgData == "transmit end".encode("utf-8"):
            break  
        imgFile.write(imgData)
    imgFile.close()






def client_server(account, connl):
    global current_client_dict
    global chatroom_client_dict
    global ttt_wait_dict
    data = (MySQLFun.get_user_data()[account], account)
    connl.send(str(data).encode("utf-8"))
    grade = MySQLFun.get_user_data()[account][1]
    path = "img_store\\grade{}.jpg" .format(grade)
    send_img(connl, path)
    
    while True:
        command = connl.recv(1024).decode("utf-8")
        if command == "00000":
            
            del current_client_dict[account]
            connl.close()
            print("{} is disconnect" .format(account))
            break
        
        elif command == "00001":
            
            img_data_dict = MySQLFun.get_img_info()
            connl.send(str(img_data_dict).encode("utf-8"))
            
        elif command == "00002":
            
            fileImg_name = connl.recv(1024).decode("utf-8")
            img_store_list = getFilePath("face_img_store")
            check_img_store_list = []
            for name in img_store_list:
                check_img_store_list.append(name[15:])
            if fileImg_name not in check_img_store_list:
                connl.send("can send img".encode("utf-8"))
                file_img_path = "face_img_store\\"+fileImg_name
                recv_img(connl, file_img_path)   
                engine = load_engine("face_feature.p")#!!!
                boxes, names = engine.make_prediction(file_img_path)
                boxes = list(boxes)
                for i in range(len(boxes)):
                    boxes[i] = list(boxes[i])
                names = names[0]
                nowtime = MySQLFun.getTime()
                img_face_data = (boxes, names, fileImg_name, nowtime, nowtime+"Untitled")
                connl.send(str(img_face_data).encode("utf-8"))
                MySQLFun.insert_to_img_info(names, fileImg_name, nowtime, nowtime+"Untitled")
                img_data_dict = MySQLFun.get_img_info()
                connl.send(str(img_data_dict).encode("utf-8"))     
            else:
                connl.send("img is exist".encode("utf-8"))
        
        elif command == "00003":
            
            nick_name = connl.recv(1024).decode("utf-8")
            img_data_dict = MySQLFun.get_img_info()
            connl.send(img_data_dict[nick_name][1].encode("utf-8"))
            send_img(connl, "face_img_store\\" + img_data_dict[nick_name][1])
            engine = load_engine("face_feature.p")
            boxes, names = engine.make_prediction("face_img_store\\" + img_data_dict[nick_name][1])#!!!
            boxes = list(boxes)
            for i in range(len(boxes)):
                boxes[i] = list(boxes[i])
            names = names[0]
            img_face_data2 = (boxes, names, img_data_dict[nick_name][1], img_data_dict[nick_name][2], nick_name)
            connl.send(str(img_face_data2).encode("utf-8"))
        
        elif command == "00004":
            
            new_name = connl.recv(1024).decode("utf-8")
            old_name = connl.recv(1024).decode("utf-8")
            check_dict = MySQLFun.get_img_info()
            if old_name in check_dict:
                MySQLFun.update_img_info_Nick_name(new_name, old_name)
                connl.send("config".encode("utf-8"))
                new_img_data_dict = MySQLFun.get_img_info()
                connl.send(str(new_img_data_dict).encode("utf-8"))
            else:
                connl.send("same in db".encode("utf-8"))
        
        elif command == "00005":
            
            nick_name = connl.recv(1024).decode("utf-8")
            img_data_dict = MySQLFun.get_img_info()
            remove("face_img_store\\" + img_data_dict[nick_name][1])
            MySQLFun.delete_img_info(nick_name)
            new_img_data_dict = MySQLFun.get_img_info()
            connl.send(str(new_img_data_dict).encode("utf-8"))
        
        elif command == "00006":
            
            for client in chatroom_client_dict:
                chatroom_client_dict[client].send("{} add the chatroom...".format(account).encode("utf-8"))
            chatroom_client_dict[account] = connl
            while True:
                msg = connl.recv(1024).decode("utf-8")
                if msg == "00000exit":
                    connl.send("00000exit".encode("utf-8"))
                    del chatroom_client_dict[account]
                    for client in chatroom_client_dict:
                        chatroom_client_dict[client].send("{} exit the chatroom...".format(account).encode("utf-8"))
                    break
                else:
                    for client in chatroom_client_dict:
                        chatroom_client_dict[client].send("{}: {}".format(account, msg).encode("utf-8"))
                    MySQLFun.inser_to_chatroom_record(account, msg)
        
        elif command == "00007":
            
            phone_list = eval(connl.recv(1024).decode("utf-8"))
            for phone in phone_list:
                MySQLFun.insert_to_phone_record(phone)
        
        elif command == "00008":
            
            password_data = eval(connl.recv(1024).decode("utf-8"))
            password = password_data[0]
            new_password = password_data[1]
            password = MySQLFun.hash256Encode(password)
            new_password = MySQLFun.hash256Encode(new_password)
            check_pw = MySQLFun.get_account_password()
            if check_pw[account] == password:
                connl.send("change password".encode("utf-8"))
                MySQLFun.update_account_password(new_password, account)
            else:
                connl.send("error password".encode("utf-8"))
        
        elif command == "00009":
            
            user_data = MySQLFun.get_user_data()
            user_name_list = []
            for name in user_data:
                user_name_list.append(name)
            connl.send(str(user_name_list).encode("utf-8"))
        
        elif command == "00010":
            
            user_name_dict = MySQLFun.get_user_data()
            user_name = connl.recv(1024).decode("utf-8")
            if user_name in user_name_dict:
                s_data = (user_name, user_name_dict[user_name])
                connl.send(str(s_data).encode("utf-8"))
            else:
                connl.send("no name in db".encode("utf-8"))
        
        elif command == "00011":
            
            set_user_data = eval(connl.recv(1024).decode("utf-8"))
            if set_user_data[0] in MySQLFun.get_user_data():
                try:
                    content = int(set_user_data[2])
                    MySQLFun.update_user_data(set_user_data[1], content, set_user_data[0])
                    connl.send("change successfully".encode("utf-8"))
                except ValueError:
                    connl.send("input error".encode("utf-8"))
            else:
                connl.send("name not in db".encode("utf-8"))
        
        elif command == "00012":
            
            del_account = connl.recv(1024).decode("utf-8")
            if del_account in MySQLFun.get_user_data():
                MySQLFun.delete_user_data_account(del_account)
                MySQLFun.delete_account_password_account(del_account)
                connl.send("delete successfully".encode("utf-8"))
            else:
                connl.send("name3 not in db".encode("utf-8"))
            

                

            
                
        

def check_password(connl, addr):
    global current_client_dict
    error_count = 1
    while True:
        user_data = connl.recv(1024).decode("utf-8")
        if user_data == "00000":
            connl.close()
            print("{} is disconnect" .format(addr))
            break
        else:
            account_password = eval(user_data)
            if len(account_password) == 2:
                account = account_password[0]
                password = account_password[1]
                password = MySQLFun.hash256Encode(password)
                password_dict = MySQLFun.get_account_password()
                if account in password_dict:
                    if password_dict[account] == password:
                        if account not in current_client_dict:
                            connl.send("correct password".encode("utf-8"))
                            print("{} welcome to login!" .format(account))
                            current_client_dict[account] = connl
                            tcs = threading.Thread(target=client_server, args=(account, connl), daemon=True)
                            tcs.start()
                            break
                        else:
                            if error_count == 3:
                                connl.send("881".encode("utf-8"))
                                connl.close()
                                print("{} is disconnect" .format(addr))
                                break
                            else:
                                connl.send("alreadly connect".encode("utf-8"))
                                print("{} alreadly connect: {}" .format(addr, error_count))
                                error_count += 1
                            
                    else:
                        if error_count == 3:
                            connl.send("881".encode("utf-8"))
                            connl.close()
                            print("{} is disconnect" .format(addr))
                            break
                        else:
                            connl.send("error password".encode("utf-8"))
                            print("{} input an error password: {}" .format(addr, error_count))
                            error_count += 1
                else:
                    if error_count == 3:
                        connl.send("881".encode("utf-8"))
                        connl.close()
                        print("{} is disconnect" .format(addr))
                        break
                    else:
                        connl.send("no account".encode("utf-8"))
                        print("{} input an error account: {}" .format(addr, error_count))
                        error_count += 1
            else:
                newaccount = account_password[1]
                newpassword = account_password[2]
                password_dict = MySQLFun.get_account_password()
                if newaccount not in password_dict:
                    MySQLFun.insert_to_account_password(newaccount, newpassword)
                    connl.send("alreadly create new account".encode("utf-8"))
                    MySQLFun.insert_to_user_data(newaccount, 0, 1)
                else:
                    connl.send("same account in db".encode("utf-8"))
                






def accept_client(sock):
    while True:
        connl, addr = sock.accept()
        checkCode = connl.recv(1024).decode("utf-8")
        if checkCode == "157sfff9345s17at86322srr564":
            connl.send("10000".encode("utf-8"))
            print("{} is legal connection" .format(addr))
            tcp = threading.Thread(target=check_password, args=(connl, addr), daemon=True)
            tcp.start()
        else:
            connl.close()