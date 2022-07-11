from http import client
import json
from logging import exception
import threading
from socket import *
from time import ctime
from cmd import Cmd
import struct
import os
import time
import pyaudio
import wave
import sys
from tkinter import Listbox, Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox, ttk, filedialog
from pathlib import Path

lock = threading.Lock()
Serverip = '47.112.132.50'
LANip = '127.0.0.1'
LANip = '47.112.132.50'
LANip = '20.187.91.251'
LANip = '127.0.0.1'
#LANip = '47.112.132.50'
#·LANip = '121.37.95.51'

Serverport = 9092
Fileport = 12389
audio_port = 9090
flag = 0
allusers = {}


class Client():

    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.file_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((LANip, Serverport))
        self.file_socket.connect((LANip, Fileport))
        self.username = ""
        self.audioflag = 0
        self.sendfile_flag = '0'

    def set_main_frm(self, frm):
        self.main_fff = frm

    def quit(self):
        self.client_socket.send(json.dumps({'type': "quit"}))
        self.client_socket.close()

    def login(self, Username, Password):
        self.client_socket.send(json.dumps({'type': 'login', 'username': Username,
                                            'password': Password}).encode())
        receive_data = self.client_socket.recv(1024).decode()
        js = json.loads(receive_data)
        return js

    def register(self, Username, Password):
        self.client_socket.send(json.dumps({'type': 'register', 'username': Username,
                                            'password': Password}).encode())
        receive_data = self.client_socket.recv(1024).decode()
        js = json.loads(receive_data)
        return js

    def receive_data_thread(self):
        print("now receiving data")
        while True:
            # print("receiving data ...")
            receive_data = None
            try:
                receive_data = self.client_socket.recv(1024).decode()
            except Exception as e:
                print("new client error:", e)
                break
            if not receive_data:
                continue
            try:
                js = json.loads(receive_data)
            except Exception as e:
                print("js wrong:", e)
                continue
            print("get pkt:", js)
            if js['type'] == 'alluser':
                self.alluser = js['msg1'].split(' ')
                self.onlinepeo = js['msg2'].split(' ')
                self.alluser.remove('')
                self.alluser.append('all')
                self.onlinepeo.remove('')
                print(self.alluser)
                print(self.onlinepeo)
                # update the Online list
                self.main_fff.Menu_select_people['value'] = tuple(self.alluser)
                self.main_fff.online_text.delete(0, "end")
                for i in self.onlinepeo:
                    self.main_fff.online_text.insert("end", i)
            elif js['type'] == 'offline':
                person = js['msg']
                print(person, " is offline")
                # tip information
                self.main_fff.outputgroup.config(state="normal")
                self.main_fff.outputgroup.insert("end", '\n <system> ' + person + '  is offline')
                self.main_fff.outputgroup.config(state="disable")
                """ try:
                    if person in self.onlinepeo:
                        self.onlinepeo.remove(person)
                    self.main_fff.online_text.delete(0,"end")
                    for i in self.onlinepeo:
                        self.main_fff.online_text.insert("end",i)
                except Exception as e:
                    print("offline msg error",e)     """
            elif js['type'] == 'p_msg':
                data = "(private message) " + js['from']
                data = data + ':' + js['msg']
                print(data)
                self.main_fff.outputgroup.config(state="normal")
                self.main_fff.outputgroup.insert("end", '\n <Private msg> User ' + js['from'] + ':')
                self.main_fff.outputgroup.insert("end", '\n ' + js['msg'])
                self.main_fff.outputgroup.config(state="disable")
            elif js['type'] == 'msgback':
                data = "(private message wrong) " + js['msg']
                self.main_fff.outputgroup.config(state="normal")
                self.main_fff.outputgroup.insert("end", '\n <private message wrong> ' + js['msg'])
                self.main_fff.outputgroup.config(state="disable")
                print(data)
            elif js['type'] == 'a_msg':
                data = "(group message) " + js['from'] + ':' + js['msg']
                print(data)
                self.main_fff.outputgroup.config(state="normal")
                self.main_fff.outputgroup.insert("end", '\n <Group msg> User ' + js['from'] + ' :')
                self.main_fff.outputgroup.insert("end", '\n ' + js['msg'])
                self.main_fff.outputgroup.config(state="disable")
            elif js['type'] == 'online':
                person = js['msg']
                print(person, " is online")
                # tip information
                self.main_fff.outputgroup.config(state="normal")
                self.main_fff.outputgroup.insert("end", '\n <system> ' + person + ' is online')
                self.main_fff.outputgroup.config(state="disable")
            elif js['type'] == 'fileDir':
                if js['type'] == "0":
                    continue
                treceive_data = self.client_socket.recv(1024).decode()
                js2 = json.loads(treceive_data)
                try:
                    msg = js2['msg']
                except Exception as e:
                    print("e")
                if (msg == "NULL"):
                    continue
                data1 = msg.split("#!")
                i = 0
                while i < len(data1) - 1:
                    self.main_fff.File_d_directory[data1[i]] = data1[i + 1]
                    i = i + 2
                print("z1", self.main_fff.File_d_directory)

    def receive_file_thread(self):
        while True:
            print("receiving file data ...")
            receive_data = None
            try:
                receive_data = self.file_socket.recv(1024).decode()
            except Exception as e:
                print("new client error:", e)
                break
            if not receive_data:
                continue
            try:
                js = json.loads(receive_data)
            except Exception as e:
                print("js wrong:", e)
                continue
            print("get file pkt:", js)
            if js['type'] == 'Permitted_file_trans':
                self.main_fff.file_button.config(state='disable')  # Lock
                self.main_fff.down_load_button.config(state='disable')  # Lock
                send_file = open(self.filename, "rb")
                alldata = send_file.read()
                size = len(alldata)
                print(size)
                # self.file_socket.send(json.dumps({'size':str(size),'file':self.filename}).encode())

                header = bytes(json.dumps({'size': str(size), 'file': self.single_name}).encode())
                header_len = len(header)
                data_header_len = struct.pack('i', header_len)

                self.file_socket.send(data_header_len)
                self.file_socket.send(header)

                receive_datalen = self.file_socket.recv(4)
                length = struct.unpack('i', receive_datalen)[0]
                receive_data = self.file_socket.recv(length).decode()
                js1 = json.loads(receive_data)
                beginsize1 = js1['size']
                beginsize = int(beginsize1)
                print("beginsize", beginsize)

                leftsize = size - beginsize
                chunksize = 1024 * 100
                sendsize = 0
                while sendsize != leftsize:
                    if leftsize - sendsize < chunksize:
                        self.file_socket.sendall(alldata[sendsize + beginsize
                                                         :sendsize + beginsize + leftsize])
                        sendsize = leftsize
                    else:
                        self.file_socket.sendall(alldata[sendsize + beginsize:
                                                         sendsize + beginsize + chunksize])
                        sendsize = sendsize + chunksize
                    self.main_fff.processbar['value'] = int((beginsize + sendsize) / size * 120)
                    if self.sendfile_flag == '0':
                        temp_flag = struct.pack('i', 0)
                        print("Already send size:", sendsize)
                        self.file_socket.send(temp_flag)
                        messagebox.showwarning(title="Warnings", message="Sending has been interrupt")
                        break
                    else:
                        temp_flag = struct.pack('i', 1)

                    self.file_socket.send(temp_flag)
                # time.sleep(0.1)
                messagebox.showwarning(title="Tips", message="Sending Done")
                self.main_fff.processbar['value'] = 0
                print("send Done")
                self.main_fff.file_button.config(state='normal')  # unLock
                self.main_fff.down_load_button.config(state='normal')  # UnLock
            elif js['type'] == "downfile":

                receive_datalen = self.file_socket.recv(4)
                length = struct.unpack('i', receive_datalen)[0]
                receive_data = self.file_socket.recv(length).decode()
                js1 = json.loads(receive_data)
                print("new file header pkt", js1)
                size = int(js1['size'])
                fromwho = js1['from']
                file_name = js1['file']
                path = os.getcwd()
                filepath1 = path + "/" + self.username
                filepath2 = filepath1 + "/" + fromwho
                if not os.path.exists(filepath1):
                    os.mkdir(filepath1)
                if not os.path.exists(filepath2):
                    os.mkdir(filepath2)
                Abs_filename = filepath2 + "/" + file_name
                if not os.path.exists(Abs_filename):
                    nowsize = 0
                else:
                    temp_read_file = open(Abs_filename, "rb")
                    temp_alldata = temp_read_file.read()
                    nowsize = len(temp_alldata)
                    temp_read_file.close()
                header = bytes(json.dumps({'size': str(nowsize)}).encode())
                header_len = len(header)
                data_header_len = struct.pack('i', header_len)
                self.file_socket.send(data_header_len)
                self.file_socket.send(header)
                leftsize = size - nowsize
                chunksize = 1024 * 100
                alldata = b''

                print("begin Downloading")
                recv_data = self.file_socket.recv(10)
                total_data = alldata + recv_data
                length = len(recv_data)
                with open(Abs_filename, "ab") as f:
                    f.write(total_data)
                while len(recv_data) > 0:
                    data = self.file_socket.recv(100000)
                    # print(len(data))
                    length += len(data)
                    with open(Abs_filename, "ab") as f:
                        f.write(data)
                    total_data += data
                    # print("正在接收文件-%s --%.2f" % (Abs_filename, length / size * 100.0) + "%")
                    if length == size:
                        break
                print("\n" + "Download down")
                messagebox.showwarning(title="Tips", message="Download Done")
                # aim_file=open(Abs_filename,'ab+')
                # aim_file.write(alldata)
                f.close()

    def getstate_thread(self):
        time.sleep(1)
        self.do_getallstate()

    def do_getallstate(self):
        lock.acquire()
        self.client_socket.send(json.dumps({'type': 'getstate'}).encode())
        lock.release()

    def do_quit(self):
        lock.acquire()
        self.client_socket.send(json.dumps({'type': 'offline'}).encode())
        lock.release()
        self.client_socket.close()
        self.file_socket.close()

    def do_send_data_to(self, name, msg):

        if name != "all":
            # ("send message to",args[0])
            lock.acquire()
            self.client_socket.send(json.dumps({'type': 'p_msg', 'msg': msg, 'to': name}).encode())
            lock.release()
        else:
            lock.acquire()
            self.client_socket.send(json.dumps({'type': 'a_msg', 'msg': msg}).encode())
            lock.release()

    def do_joinaudio(self):
        self.audio_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.audio_socket.connect((LANip, audio_port))
            print("link up")
        except Exception as e:
            print("erroe", e)
            print("link down")
            return
        self.audioflag = 1
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        RATE = 16000
        CHANNELS = 1
        p = pyaudio.PyAudio()
        stream1 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
        stream2 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        thread1 = threading.Thread(target=Rtime_Decording, args=(stream1, self.audio_socket), daemon=True)
        thread2 = threading.Thread(target=Rtime_Recording, args=(stream2, self.audio_socket), daemon=True)
        thread1.start()
        thread2.start()
        self.audiocs = [self.audio_socket, stream1, stream2, p]

    def do_quitaudio(self):
        try:
            if len(self.audiocs) > 0:
                self.audioflag = 0
                self.audiocs[0].close()
                self.audiocs[1].close()
                self.audiocs[2].close()
                self.audiocs[3].terminate()
                self.audiocs = []
                print("you quit audio group")

        except Exception as e:
            print("quit audio error", e)

    def do_sendfile(self, filename, name):
        try:

            self.filename = filename

            splitname = filename.split('/')
            single_name = splitname[len(splitname) - 1]
            self.single_name = single_name
            print("the file is", single_name)
            send_file = open(filename, "rb")

            send_file.close()
        except Exception as e:
            print("open wrong", e)
            return
        self.file_socket.send(json.dumps({'type': "file", 'to': name,
                                          'filename': single_name,
                                          'from': self.username}).encode())

    def do_getfile(self):

        lock.acquire()
        self.client_socket.send(json.dumps({'type': 'getfile'}).encode())
        lock.release()
        self.main_fff.File_Directory.delete(0, "end")
        t = self.main_fff.File_d_directory.keys()

        for i in t:
            self.main_fff.File_Directory.insert("end", i)
        self.File_D_level = 0

    def do_downfile(self, fromwho, filename):
        print("from", fromwho)
        print("filename", filename)
        self.file_socket.send(json.dumps({'type': "download", 'from': fromwho,
                                          'filename': filename,
                                          'to': self.username}).encode())


class login_frm():
    def __init__(self, myclient):
        self.window = Tk()
        self.window.geometry("730x415")
        self.window.configure(bg="#4153FB")
        self.myclient = myclient
        self.set_all_icons(self.window)

    def set_all_icons(self, window):
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path("./icons/login")

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        # canvas settings
        canvas = Canvas(
            window,
            bg="#4153FB",
            height=415,
            width=730,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            354.99999999999994,
            0.0,
            730.0,
            415.0,
            fill="#FFFFFF",
            outline=""
        )
        canvas.create_text(
            377.99999999999994,
            386.0,
            anchor="nw",
            text="No Account?",
            fill="#000000",
            font=("Inter Bold", 15 * -1)
        )
        # register part
        register_button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        register_button_1 = Button(
            image=register_button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.register_func,
            relief="flat"
        )
        register_button_1.place(
            x=478.99999999999994,
            y=385.0,
            width=43.13726806640625,
            height=18.0
        )
        # login part
        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        login_button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.login_func,
            relief="flat"
        )
        login_button_2.place(
            x=427.99999999999994,
            y=310.0,
            width=229.0,
            height=46.0
        )
        # password entry
        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            531.5,
            243.5,
            image=entry_image_1
        )
        password_entry_1 = Entry(
            bd=0,
            bg="#F1F0F0",
            highlightthickness=0,
            show='*'
        )
        password_entry_1.place(
            x=374.99999999999994,
            y=216.0 + 30,
            width=313.0,
            height=23.0
        )
        self.password_entry = password_entry_1
        # username entry
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            531.5,
            174.5,
            image=entry_image_2
        )
        username_entry_2 = Entry(
            bd=0,
            bg="#EFEFEF",
            highlightthickness=0
        )
        username_entry_2.place(
            x=374.99999999999994,
            y=147.0 + 30,
            width=313.0,
            height=23.0
        )
        self.username_entry = username_entry_2
        # text
        canvas.create_text(
            377.99999999999994,
            156.0,
            anchor="nw",
            text="username",
            fill="#000000",
            font=("Inter ExtraBold", 15 * -1)
        )
        canvas.create_text(
            377.99999999999994,
            225.0,
            anchor="nw",
            text="password",
            fill="#000000",
            font=("Inter ExtraBold", 15 * -1)
        )
        canvas.create_text(
            364.99999999999994,
            38.0,
            anchor="nw",
            text="Join",
            fill="#000000",
            font=("Inter ExtraBold", 48 * -1)
        )
        canvas.create_text(
            478.99999999999994,
            50.0,
            anchor="nw",
            text="Now",
            fill="#000000",
            font=("Inter ExtraBold", 48 * -1)
        )
        canvas.create_text(
            7.999999999999943,
            67.0,
            anchor="nw",
            text="Welcome to xxXXxx",
            fill="#FFFFFF",
            font=("Inter Bold", 20 * -1)
        )
        canvas.create_rectangle(
            7.999999999999943,
            93.0,
            94.99999999999994,
            96.0,
            fill="#FFFFFF",
            outline=""
        )

        # self.window.resizable(False, False)
        self.window.mainloop()

    def login_func(self):
        Username = self.username_entry.get()
        Password = self.password_entry.get()
        if ' ' in Username or ' ' in Password:
            messagebox.showwarning(title="Warnings", message="There can not be space in username and password")
            return
        js = self.myclient.login(Username, Password)
        if js['state'] == 'succeed':
            flag = 1
            self.myclient.username = Username
            messagebox.showwarning(title="Success", message='success,' + js['msg'])
            data_thread = threading.Thread(target=self.myclient.receive_data_thread, daemon=True)
            data_thread.start()
            file_thread = threading.Thread(target=self.myclient.receive_file_thread, daemon=True)
            file_thread.start()
            self.window.destroy()
            my_main_frm = main_frm(self.myclient)
        else:
            messagebox.showwarning(title="Warnings", message=js['msg'])

    def register_func(self):
        self.window.destroy()
        my_register_frm = register_frm(self.myclient)


class register_frm():
    def __init__(self, myclient):
        self.myclient = myclient
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path("./icons/reg")

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        print(ASSETS_PATH)
        self.window = window = Tk()

        window.geometry("375x415")
        window.configure(bg="#FFFFFF")
        canvas = Canvas(
            window,
            bg="#FFFFFF",
            height=415,
            width=375,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            0.0,
            0.0,
            375.0,
            415.0,
            fill="#FFFFFF",
            outline="")

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png")
        )
        # passwordEntry
        entry_bg_1 = canvas.create_image(
            176.5,
            243.5,
            image=entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#E4E4E4",
            highlightthickness=0,
            show='*'
        )
        entry_1.place(
            x=20.0,
            y=216.0 + 30,
            width=313.0,
            height=23.0
        )
        self.password_entry = entry_1
        # usernameEntry
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            176.5,
            174.5,
            image=entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#E4E4E4",
            highlightthickness=0
        )
        entry_2.place(
            x=20.0,
            y=147.0 + 30,
            width=313.0,
            height=23.0
        )
        self.username_entry = entry_2

        canvas.create_text(
            23.0,
            156.0,
            anchor="nw",
            text="username",
            fill="#000000",
            font=("Inter ExtraBold", 15 * -1)
        )

        canvas.create_text(
            23.0,
            225.0,
            anchor="nw",
            text="password",
            fill="#000000",
            font=("Inter ExtraBold", 15 * -1)
        )

        canvas.create_text(
            10.0,
            38.0,
            anchor="nw",
            text="Join",
            fill="#000000",
            font=("Inter ExtraBold", 48 * -1)
        )

        canvas.create_text(
            339.0,
            176.0,
            anchor="nw",
            text=":)",
            fill="#000000",
            font=("Inter ExtraBold", 48 * -1)
        )

        canvas.create_text(
            141.0,
            55.0,
            anchor="nw",
            text="Now",
            fill="#000000",
            font=("Inter ExtraBold", 48 * -1)
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.register_func,
            relief="flat"
        )
        button_1.place(
            x=73.0,
            y=310.0,
            width=229.0,
            height=46.0
        )
        window.resizable(False, False)
        window.mainloop()

    def register_func(self):
        Username = self.username_entry.get()
        Password = self.password_entry.get()
        if ' ' in Username or ' ' in Password:
            messagebox.showwarning(title="Warnings", message="There can not be space in username and password")
            return
        js = self.myclient.register(Username, Password)

        if js['state'] == 'succeed':
            flag = 1
            self.myclient.username = Username
            messagebox.showwarning(title="Success", message=js['msg'])
            data_thread = threading.Thread(target=self.myclient.receive_data_thread, daemon=True)
            data_thread.start()
            file_thread = threading.Thread(target=self.myclient.receive_file_thread, daemon=True)
            file_thread.start()
            self.window.destroy()
            my_main_frm = main_frm(self.myclient)
        else:
            messagebox.showwarning(title="Warnings", message=js['msg'])


class main_frm():

    def __init__(self, myclient):
        self.audio_state = 0
        self.myclient = myclient
        # create a thread getting state information
        getstate_thread = threading.Thread(target=self.myclient.getstate_thread, daemon=True)
        getstate_thread.start()

        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path("./icons/main")
        self.icons_path = ASSETS_PATH

        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        window = Tk()
        self.window = window
        self.myclient.set_main_frm(self)
        window.geometry("800x800")
        window.configure(bg="#FFFFFF")

        canvas = Canvas(
            window,
            bg="#FFFFFF",
            height=800,
            width=800,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            400.0,
            400.0,
            image=image_image_1
        )

        image_image_2 = PhotoImage(
            file=relative_to_assets("image_2.png"))
        image_2 = canvas.create_image(
            272.78125,
            297.5625,
            image=image_image_2
        )

        image_image_3 = PhotoImage(
            file=relative_to_assets("image_3.png"))
        image_3 = canvas.create_image(
            272.78125,
            698.3125,
            image=image_image_3
        )

        image_image_4 = PhotoImage(
            file=relative_to_assets("image_4.png"))
        image_4 = canvas.create_image(
            273.0,
            611.0,
            image=image_image_4
        )

        # send file button
        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.send_file,
            relief="flat"
        )
        self.file_button = button_1
        button_1.place(
            x=330.0,
            y=597.0,
            width=30.0,
            height=30.0
        )
        # Audio talk Button
        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        self.audio_audio_on_icons = button_image_2
        self.audio_audio_off_icons = PhotoImage(
            file=relative_to_assets("image_audiodown.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.audio_talk,
            relief="flat"
        )
        self.audio_button = button_2
        button_2.place(
            x=290.0,
            y=597.0,
            width=30.0,
            height=30.0
        )
        # Updata Button
        update_image_2 = PhotoImage(
            file=relative_to_assets("update.png"))
        updata_button = Button(
            image=update_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.myclient.do_getallstate,
            relief="flat"
        )
        updata_button.place(
            x=250.0,
            y=597.0,
            width=30.0,
            height=30.0
        )
        # send msg button
        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.send_func,
            relief="flat"
        )
        self.audio_msg = button_3
        button_3.place(
            x=472.0,
            y=765.0,
            width=67.125,
            height=33.0625
        )
        # group output
        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            273.5,
            314.5,
            image=entry_image_1
        )
        output1 = Text(
            bd=0,
            bg="#DEE4E8",
            highlightthickness=0,
            state='disable'

        )
        output1.place(
            x=21.0,
            y=96.0 + 25,
            width=505.0,
            height=435.0 - 50
        )
        self.outputgroup = output1
        # input
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            272.0,
            699.0,
            image=entry_image_2
        )
        input1 = Text(
            bd=0,
            bg="#EEEEEF",
            highlightthickness=0
        )
        input1.place(
            x=15.0,
            y=651.0 + 15,
            width=514.0,
            height=94.0 - 30
        )
        self.input1 = input1
        # Send to Text
        Sendto = Text(
            bd=0,
            bg="#FFFFFF",
            highlightthickness=0,
        )
        Sendto.insert("1.0", "Send to")
        Sendto.config(state='disable')
        Sendto.place(
            x=126.0 - 100,
            y=605.0,
            width=70,
            height=20.0
        )
        # Menu for select people
        cbox = ttk.Combobox(window)
        cbox.place(
            x=200.0 - 100,
            y=597.0,
            width=130.0,
            height=30.0
        )
        cbox['value'] = ('all',)
        cbox.current(0)
        self.Menu_select_people = cbox

        image_Audio_5 = PhotoImage(
            file=relative_to_assets("Audio_image_5.png"))
        image_5 = canvas.create_image(
            673.0,
            385.0,
            image=image_Audio_5
        )

        image_online_6 = PhotoImage(
            file=relative_to_assets("Online_image_6.png"))
        image_6 = canvas.create_image(
            673.0,
            108.0,
            image=image_online_6
        )

        canvas.create_text(
            609.0,
            99.0,
            anchor="nw",
            text="Online people",
            fill="#FFFFFF",
            font=("Inter", 20 * -1)
        )

        canvas.create_text(
            611.0,
            373.0,
            anchor="nw",
            text="File Directory",
            fill="#000000",
            font=("Inter", 20 * -1)
        )

        # _stop_filesend
        button_image_4 = PhotoImage(
            file=relative_to_assets("file_down.png"))
        button_4 = Button(
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.file_pause,
            relief="flat"
        )
        button_4.place(
            x=500.0,
            y=597.0,
            width=30.0,
            height=30.0
        )
        # file_process bar
        self.processbar = ttk.Progressbar(window,
                                          length=120
                                          )
        self.processbar.place(
            x=370.0,
            y=602.0,

        )
        # onlinePeople
        online_image_3 = PhotoImage(
            file=relative_to_assets("online_bg.png"))
        entry_bg_3 = canvas.create_image(
            673.0,
            218.5,
            image=online_image_3
        )
        online_3 = Listbox(window,
                           bd=0,
                           bg="#406C96",
                           fg="#FFFFFF",
                           highlightthickness=0
                           )

        self.online_text = online_3
        online_3.place(
            x=546.0,
            y=123.0,
            width=254.0,
            height=189.0
        )
        # File Directory
        Audio_image_4 = PhotoImage(
            file=relative_to_assets("Audio_bg.png"))
        entry_bg_4 = canvas.create_image(
            673.0,
            480.0 + 30,
            image=Audio_image_4
        )
        Audio_4 = Listbox(
            bd=0,
            bg="#DEE4E8",
            fg="#000000",
            font=('microsoft yahei', 16, 'bold'),
            highlightthickness=0
        )

        self.File_Directory = Audio_4
        self.File_Directory.insert("end", 'None')
        Audio_4.place(
            x=546.0,
            y=400.0 + 30,
            width=254.0,
            height=158.0
        )
        self.File_D_level = 0
        self.File_d_directory = {}

        self.File_D_0_content = ""
        self.File_D_1_content = []

        file_directory = PhotoImage(
            file=relative_to_assets("update.png"))
        file_directory_button = Button(
            image=file_directory,
            borderwidth=0,
            highlightthickness=0,
            command=self.myclient.do_getfile,
            relief="flat"
        )
        file_directory_button.place(
            x=546,
            y=400,
            width=30,
            height=30
        )
        left_3 = PhotoImage(
            file=relative_to_assets("leftarrow.png"))
        left_button_3 = Button(
            image=left_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.theParentDir,
            relief="flat"
        )
        left_button_3.place(
            x=546 + 30 + 30,
            y=400,
            width=30,
            height=30
        )
        right_3 = PhotoImage(
            file=relative_to_assets("rightarrow.png"))
        right_button_3 = Button(
            image=right_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.theSonDir,
            relief="flat"
        )
        right_button_3.place(
            x=800 - 30 - 30 - 30,
            y=400,
            width=30,
            height=30
        )

        down_load = PhotoImage(
            file=relative_to_assets("download.png"))
        down_load_button = Button(
            image=down_load,
            borderwidth=0,
            highlightthickness=0,
            command=self.down_file,
            relief="flat"
        )
        self.down_load_button = down_load_button
        down_load_button.place(
            x=800 - 30,
            y=400,
            width=30,
            height=30
        )

        window.resizable(False, False)
        window.mainloop()

    def send_func(self):
        data = self.input1.get("1.0", "end")
        self.input1.delete("1.0", "end")
        send_to = self.Menu_select_people.get()
        print("Send msg to", send_to, "\nmsg", data)
        ##act to send msg
        self.myclient.do_send_data_to(send_to, data)

    def send_file(self):
        self.file_button.config(state='disable')  # Lock
        self.down_load_button.config(state='disable')  # Lock
        self.myclient.sendfile_flag = '1'
        send_to = self.Menu_select_people.get()
        filename = filedialog.askopenfilename()
        print("Send file to", send_to, " file name:", filename)

        ##act to send file
        self.myclient.do_sendfile(filename, send_to)
        self.processbar['value'] = 0
        self.file_button.config(state='normal')  # unLock
        self.down_load_button.config(state='normal')  # unLock

    def audio_talk(self):
        if self.myclient.audioflag != 1:
            print("Joining audio talk...")
            self.audio_button.config(state='disable')
            self.audio_button.config(image=self.audio_audio_off_icons)
            self.myclient.do_joinaudio()
            self.audio_button.config(state='normal')
            # change the icon
        else:
            print("quiting audio talk...")
            self.audio_button.config(state='disable')
            self.audio_button.config(image=self.audio_audio_on_icons)
            self.myclient.do_quitaudio()
            self.audio_button.config(state='normal')

    def quit_func(self):
        print("quit")

    def file_pause(self):
        print("file_send_pause")
        lock.acquire()
        self.myclient.sendfile_flag = '0'
        lock.release()

    def theParentDir(self):
        print()
        if self.File_D_level == 0:
            messagebox.showwarning(title="Warnings", message="Already in Partent Directory")
        else:
            t = self.File_d_directory.keys()
            self.File_Directory.delete(0, "end")
            for i in t:
                self.File_Directory.insert("end", i)
            self.File_D_level = 0

    def theSonDir(self):
        if self.File_D_level == 1:
            messagebox.showwarning(title="Warnings", message="Already in Son Directory")
        try:
            data = self.File_Directory.get(self.File_Directory.curselection())
        except Exception as e:
            messagebox.showwarning(title="Warnings", message=
            "No Selected Directory")
            print(e)
            return
        self.File_D_0_content = data
        str = self.File_d_directory[data]
        print("str ", str)
        data1 = str.split("*#")
        print("dict ", self.File_d_directory)
        self.File_Directory.delete(0, "end")
        for i in range(0, len(data1) - 1):
            self.File_Directory.insert("end", data1[i])
        self.File_D_level = 1

    def down_file(self):
        print("down file")
        if self.File_D_level == 0:
            messagebox.showwarning(title="Warnings", message="Selecting a Directory")
            return
        else:
            try:
                data = self.File_Directory.get(self.File_Directory.curselection())
            except Exception as e:
                messagebox.showwarning(title="Warnings", message=
                "No Selected File")
                print(e)
                return
        self.file_button.config(state='disable')  # Lock
        self.down_load_button.config(state='disable')  # Lock
        self.myclient.do_downfile(self.File_D_0_content, data)
        self.file_button.config(state='normal')  # unLock
        self.down_load_button.config(state='normal')  # unLock


def Rtime_Recording(stream, cs):
    while True:
        try:
            data = stream.read(1024)
            cs.sendall(data)
        except Exception as e:
            print("Rtime Recodring", error)
            break


def Rtime_Decording(stream, cs):
    while True:
        try:
            data = cs.recv(1024)
        except Exception as e:
            print("Rtime Decodring1", error)
            break
        try:
            stream.write(data)
        except Exception as e:
            print("Rtime Decodring2", error)
            break


my_client = Client()
my_login_frm = login_frm(my_client)
