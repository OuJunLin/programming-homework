import socket
import threading
import connectFun

s = socket.socket()
print("server running")
host = socket.gethostbyname(socket.gethostname())
port = 2022
print()
print("Server info:\n", "---"*10)
print("Server IP: {}\nServer Port: {}" .format(host, port))
print("---"*10)
print("Server command:")
print("'0': stop server")
print("'1': print current clients")
print("---"*10)
s.bind((host, port))
print("listen...")
s.listen(5)



def server_command():
    global current_client_dict
    while True:
        n = input()
        if n == "0":
            break
        elif n == "1":
            print("---"*10)
            print("client number: {}" .format(len(connectFun.get_current_clients())))
            for account in connectFun.get_current_clients():
                print(account)
            print("---"*10)
            


tr = threading.Thread(target=connectFun.accept_client,args=(s,), daemon=True)

try:
    tr.start()
    server_command()
except ConnectionAbortedError:
    print("connected error")

s.close()
print("server done!")
    
    
    