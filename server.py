import json
from multiprocessing import AuthenticationError
import threading
from socket import *
from time import ctime
import time
import struct
import os
ip_to_socket={}
ip_to_file_socket={}
faddr_to_caddr={}
caddr_to_faddr={}
username_password={}
online_username={}
username_socket={}
username_file_socket={}

lock = threading.Lock()
file_nowpoint={}
file_list={}
file_flag={}
file_thread_flag={}
file_con={}

class Server:
    file_socket=socket(AF_INET,SOCK_STREAM)
    server_socket=socket(AF_INET,SOCK_STREAM)
    audio_socket=socket(AF_INET,SOCK_STREAM)
    server_port=9092
    file_port=12389
    audio_port=9090

        
    def __init__(self):

        self.file_socket.bind(('',self.file_port))
        self.server_socket.bind(('',self.server_port))
        self.audio_socket.bind(('',self.audio_port))
        self.server_socket.listen(50)
        self.file_socket.listen(50)
        self.audio_socket.listen(50)
        newaudio=group_audio()
        audio_thread=threading.Thread(target=create_audio_thread,args=(newaudio,self.audio_socket),daemon=True)
        audio_thread.start() 
        #read the username and password file 
        path=os.getcwd()
        self.Authenticationfile=path+"/users.txt"
        with open(self.Authenticationfile,'r') as usersfile:
            alldata=usersfile.read()
        self.alluserdata=alldata.split()

        i=0
        while i<len(self.alluserdata):
            username_password[self.alluserdata[i]]=self.alluserdata[i+1]
            online_username[self.alluserdata[i]]=False
            i=i+2
        usersfile.close()
        
        
        

    def start(self):
        while True:
            try:
                print("now listen")
                c_socket,c_addr=self.server_socket.accept()
                f_socket,f_addr=self.file_socket.accept()
                ip_to_socket[c_addr]=c_socket
                ip_to_file_socket[c_addr]=f_socket
                print("There is a new client ip:",c_addr)
                print("There is a new filesocket ip",f_addr)
                newclient=client()
                client_thread=threading.Thread(target=create_client_thread,args=(newclient,c_addr,),daemon=True)
                client_thread.start()                
            except Exception as e:
                print("Server error",e)

def create_client_thread(newclient,addr):
    newclient.new_client_identification(addr)
def create_file_thread(newfile,addr):
    newfile.newfile(addr)
def create_audio_thread(newaudio,cs):
    newaudio.start_(cs)
class fileClient():
    def newfile(self,addr):
        file_socket=ip_to_file_socket[addr]
        while True:
            try:
                receive_data=file_socket.recv(1024).decode()
            except Exception as e:
                print("file client error:",e)
                #self.quit()
                break
            if not receive_data:
                continue
            try:
                js=json.loads(receive_data)
            except:
                continue
            print("new file pkt",js)
            if js['type']=='file':
                file_flag_temp=0
                file_socket.send(json.dumps({'type':'Permitted_file_trans'}).encode())
                
                file_name=js['filename']
                towho=js['to']
                fromwho=js['from']
                
                receive_datalen=file_socket.recv(4)
                length=struct.unpack('i',receive_datalen)[0]
                receive_data=file_socket.recv(length).decode()      
                js1=json.loads(receive_data)
                print("new file header pkt",js1)
                size=int(js1['size'])
                path = os.getcwd()
                filepath1=path+"/"+towho
                filepath2=filepath1+"/"+fromwho
                if not os.path.exists(filepath1):
                    os.mkdir(filepath1)
                if not os.path.exists(filepath2):
                    os.mkdir(filepath2)
                Abs_filename=filepath2+"/"+file_name
                if not os.path.exists(Abs_filename):
                    nowsize=0
                else:
                    temp_read_file=open(Abs_filename,"rb")
                    temp_alldata=temp_read_file.read()
                    nowsize=len(temp_alldata)
                    temp_read_file.close()
                header=bytes(json.dumps({'size':str(nowsize)}).encode())
                header_len=len(header)
                data_header_len=struct.pack('i',header_len)
                file_socket.send(data_header_len)
                file_socket.send(header)

                leftsize=size-nowsize
                chunksize=1024*100
                            
                alldata=b''
                
                print("begin Downloading")
                while(nowsize!=size):
                    if size-nowsize>chunksize:
                        receive_data=file_socket.recv(chunksize)
                        while len(receive_data)!=chunksize:
                            tempdata=receive_data
                            receive_data+=file_socket.recv(chunksize-len(tempdata))
                        print("chunksize",nowsize)
                    else:
                        receive_data=file_socket.recv(size-nowsize)
                        while len(receive_data)!=size-nowsize:
                            tempdata=receive_data
                            receive_data+=file_socket.recv(size-nowsize-len(tempdata))
                        print("size-nowsize",nowsize)
                    #print(nowsize)
                    alldata+=receive_data
                    nowsize+=len(receive_data)
                    receive_flag=file_socket.recv(4)
                    temp_flag=struct.unpack('i',receive_flag)[0]
                    if temp_flag==0:
                        break
                    else:
                        continue

                print("\n"+"Download down")
                
                aim_file=open(Abs_filename,'ab+')
                aim_file.write(alldata)
                aim_file.close()
            elif js['type']=="download":
                
                fromwhot=js['from']
                to=js['to']
                filenamet=js['filename']
                patht = os.getcwd()
                filepath1=patht+"/"+to
                filepath2=filepath1+"/"+fromwhot
                filepath3=filepath2+"/"+filenamet
                print("filepath",filepath3)
                try:
                    send_file=open(filepath3,"rb")
                    alldata=send_file.read()
                    size=len(alldata)
                except Exception as e:
                    print("Sendfile wrong",e)
                    continue
                file_socket.send(json.dumps({'type':'downfile'}).encode())
                
                header=bytes(json.dumps({'size':str(size),'file':filenamet,
                                         "from":fromwhot}).encode())
                header_len=len(header)
                data_header_len=struct.pack('i',header_len)
                file_socket.send(data_header_len)
                file_socket.send(header)
                
                receive_datalen=file_socket.recv(4)
                length=struct.unpack('i',receive_datalen)[0]
                receive_data=file_socket.recv(length).decode() 
                js1=json.loads(receive_data)
                beginsize1=js1['size']
                beginsize=int(beginsize1)
                print("beginsize",beginsize)
                leftsize=size-beginsize
                chunksize=1024*100
                sendsize=0
                
                while sendsize!=leftsize:
                    if leftsize-sendsize<chunksize:
                        file_socket.sendall(alldata[sendsize+beginsize
                                                         :sendsize+beginsize+leftsize])
                        sendsize=leftsize
                    else:
                        file_socket.sendall(alldata[sendsize+beginsize:
                                                         sendsize+beginsize+chunksize])
                        sendsize=sendsize+chunksize
                
                print("Some body download done")
                
class client():
    name=None
    c_addr=None
    f_addr=None
    def __init__(self):
        #self.new_client_identification(addr)
        print()
    def new_client_identification(self,addr):
        self.c_addr=addr
        while True:
            try:
                receive_data=ip_to_socket[addr].recv(1024).decode()
            except Exception as e:
                print("new client error:",e)
                #del ip_to_socket[self.c_addr]
                return
            if not receive_data:
                continue
            js=json.loads(receive_data)
            if js['type']=="login":
                print(addr,"is try to login")
                username=str(js['username'])
                password=str(js['password'])
                if username in username_password.keys():
                    if online_username[username]==True:
                        ip_to_socket[addr].send(json.dumps({'state':'fail','msg':'Already online,try another acount '}).encode()) #fail
                        continue
                    if password== username_password[username]:
                        ip_to_socket[addr].send(json.dumps({'state':'succeed','msg':'Having fun'}).encode()) #succeed
                        
                        username_socket[username]=ip_to_socket[addr]
                        username_file_socket[username]=ip_to_file_socket[addr]
                        online_username[username]=True
                        self.name=username
                        break                
                    else:
                        ip_to_socket[addr].send(json.dumps({'state':'fail','msg':'wrong password, you may try again'}).encode()) #fail
                        continue
                else:
                    ip_to_socket[addr].send(json.dumps({'state':'fail','msg':'no such username, you may try again or you can create a new acount'}).encode())
                    continue #fail
            elif js['type']=="register":
                print(addr,"is try to register")
                username=str(js['username'])
                password=str(js['password'])
                if username in username_password.keys():
                    ip_to_socket[addr].send(json.dumps({'state':'fail','msg':'Duplicate username, try another username'}).encode())
                    continue #fail
                else:
                    username_password[username]=password
                    
                    username_socket[username]=ip_to_socket[addr]
                    file_list[username]=0
                    file_flag[username]=False
                    username_file_socket[username]=ip_to_file_socket[addr]
                    online_username[username]=True
                    self.name=username
                    ip_to_socket[addr].send(json.dumps({'state':'succeed','msg':'succeed,and login automatically. Having fun'}).encode())
                    path=os.getcwd()
                    Authenticationfile=path+"/users.txt"
                    with open(Authenticationfile,'a+') as usersfile:
                        lock.acquire()
                        usersfile.write("\n")
                        usersfile.write(username)
                        usersfile.write(" "+password)
                        print(1)
                        usersfile.close()
                        lock.release()
                    break
            elif js['type']=="quit":#direct quit
                print(addr,"is try to quit")
                ip_to_socket[addr].close()
                del ip_to_socket[addr]
                del ip_to_file_socket[addr]

                return
        newfileclient=fileClient()
        client_thread=threading.Thread(target=create_file_thread,args=(newfileclient,self.c_addr,),daemon=True)
        client_thread.start()
        self.chat()


    def chat(self):
        #send online msg
        for user in online_username.keys():
            if online_username[user]==True and user !=self.name:
                lock.acquire()
                try:
                    
                    username_socket[user].send(json.dumps({'type':'online',
                                                           'msg':self.name}).encode())
                except Exception as e:
                    print("login data send error",e)
                lock.release()
        while True:
            receive_data=None
            try:
                receive_data=username_socket[self.name].recv(1024).decode()
            except Exception as e:
                print("chat client error:",e)
                self.quit()
                break
            if not receive_data:
                continue
            js=json.loads(receive_data)
            print("new pkt from",self.name,"js:",js)
            if js['type']=='offline':
                username_socket[self.name].close()
                online_username[self.name]=False
                del ip_to_socket[self.c_addr]
                del username_socket[self.name]
                data=self.name
                for on_name in online_username.keys():
                    if online_username[on_name]==True:
                        lock.acquire()
                        username_socket[on_name].send(json.dumps({'type':'offline','msg':data}).encode())
                        lock.release()
            elif js['type']=='p_msg':
                person=js['to']
                msg=js['msg']
                if person not in username_password.keys():
                    lock.acquire()
                    username_socket[self.name].send(json.dumps({'type':'msgback','msg':"There is no person naming"+ person}).encode())
                    lock.release()
                    continue
                if online_username[person]==True:
                    lock.acquire()
                    username_socket[person].send(json.dumps({'type':'p_msg','msg':msg,'from':self.name}).encode())
                    lock.release()
                else:
                    lock.acquire()
                    username_socket[self.name].send(json.dumps({'type':'msgback','msg': person+"is offline"}).encode())
                    lock.release()
            elif js['type']=='a_msg':
                msg=js['msg']
                for online in online_username.keys():
                    if online_username[online]==True:
                        lock.acquire()
                        try:
                            
                            username_socket[online].send(json.dumps({'type':'a_msg','msg':msg,'from':self.name}).encode())
                            
                        except:
                            print("socket wrong")
                        lock.release()
            elif js['type']=='getstate':
                data=""
                #send all online
                all_name=""
                print("now send state data to new online person")
                for name in username_password.keys():
                    all_name=all_name+name+" "
                all_name.strip(' ')
                for on_name in online_username.keys():
                    if online_username[on_name]==True:
                        data=data+on_name+" "
                data.strip(' ')
                lock.acquire()
                username_socket[self.name].send(json.dumps({'type':'alluser','msg1':all_name,'msg2':data}).encode())
                lock.release()
                print("send1 done")
            elif js['type']=='getfile':
                
                print()
                path = os.getcwd()
                filepath1=path+"/"+self.name
                str=""
                
                if not os.path.exists(filepath1):
                    lock.acquire()
                    username_socket[self.name].send(json.dumps({
                        'type':'fileDir','state':'0'}).encode())
                    lock.release()
                else:
                    lock.acquire()
                    username_socket[self.name].send(json.dumps({
                        'type':'fileDir','state':'1'}).encode())
                    time.sleep(0.1)
                    for i in os.listdir(filepath1):
                        str=str+i+"#!"
                        for j in os.listdir(filepath1+'/'+i):
                            str=str+j+"*#"
                        str=str+"#!"
                    print(str)
                    if str=="":
                        srt="NULL"  
                    username_socket[self.name].send(json.dumps({
                        'msg':str}).encode())
                    lock.release()
                
                            
                            
                            
                    
                    
                
    def quit(self):
        username_socket[self.name].close()
        online_username[self.name]=False
        try:
            del ip_to_socket[self.c_addr]
            del username_socket[self.name]
        except:
            print("quit wrong")
        for user in online_username.keys():
            if online_username[user]==True:
                lock.acquire()
                try:
                    
                    username_socket[user].send(json.dumps({'type':'offline',
                                                           'msg':self.name}).encode())
                except Exception as e:
                    print("quit error",e)
                lock.release()
                    
class group_audio():

    def __init__(self):
        self.all_users={}
        
        self.all=0
    def start_(self,cs):
        self.audio_socket=cs
        while True:
            cs,addr=self.audio_socket.accept()
            print("new audio",addr)
            self.all=self.all+1
            self.all_users[addr]=[1,cs]
            new=threading.Thread(target=self.new_client,args=(cs,addr,),daemon=True)
            new.start()
            
    def new_client(self,cs,addr):
        while True:
            try:
                audio=cs.recv(1024)
                if self.all >1:
                    lock.acquire()
                    self.send(cs,addr,audio )
                    lock.release()
            except Exception as e:
                print("error",e)
                self.all_users[addr][0]=0
                self.all=self.all-1
                cs.close()
                break
    def send(self,cs,addr,audio):
        for client in self.all_users.keys():
            if self.all_users[client][1] !=cs and self.all_users[client][0]==1:
                try:
                    self.all_users[client][1].send(audio)
                except Exception as e:
                    print("error ",e)
                    break


def main():
    my_server=Server()
    my_server.start()
main()
