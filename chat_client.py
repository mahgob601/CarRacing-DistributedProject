import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


class Client:
    connected_clients = []
    backup_host = "13.51.48.183"
    backup_port = 5561
    HOST = "13.48.195.218"
    PORT = 5560

    def __init__(self,):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please Choose a nickname", parent=msg)
        self.gui_done = False
        self.running = True

    def start_chat(self):
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title(self.nickname)
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.send_button.config(font=('Arial', 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def write(self):
        message = f"CHAT {self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def receive(self):
        print("started receiving")
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                special_message = message.split('$')
                if message == "":
                    raise Exception

                for m in special_message:
                    splitted_msg = m.split(' ')
                    print(m)

                    if splitted_msg[0] == "NEWCONN":
                        connected_clients = []
                        for x in range(1, len(splitted_msg)):
                            connected_clients.append(splitted_msg[x])
                        print(connected_clients)
                    elif m == "NICK":
                        self.sock.send(self.nickname.encode('utf-8'))
                    elif splitted_msg[0] == "CHAT":
                        if self.gui_done:
                            splitted_msg.remove("CHAT")
                            m = ""
                            for each in splitted_msg:
                                m = m + " " + each

                            self.text_area.config(state='normal')
                            self.text_area.insert('end', m)
                            self.text_area.yview('end')
                            self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break
            except:
                print("Main server crashed")
                self.sock.close()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.backup_port, self.backup_port))

                print("connected to backup server")


client = Client()
client.start_chat()
