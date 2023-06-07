import socket
import threading
import mysql.connector as myconn
import datetime
import MySQLFun

current_client_dict = {}


def get_current_clients():
    global current_client_dict
    return current_client_dict



def client_server(account, connl):
    global current_client_dict
    while True:
        command = connl.recv(1024).decode("utf-8")
        if command == "00000":
            del current_client_dict[account]
            connl.close()
            print("{} is disconnect" .format(account))
            break






def check_password(connl, addr):
    global current_client_dict
    error_count = 1
    while True:
        user_data = connl.recv(1024).decode("utf-8")
        print(user_data)
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