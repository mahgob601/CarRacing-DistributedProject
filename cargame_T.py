import random

import pygame
from time import sleep
import socket
from threading import Thread
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


class ChatClient:
    connected_clients = []
    backup_host = "13.51.48.183"
    backup_port = 5561
    HOST = "13.48.195.218"
    PORT = 5560

    def __init__(self, nick):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.gui_done = False
        self.running = True
        self.nickname = nick

    def start_chat(self):
        gui_thread = Thread(target=self.gui_loop)
        receive_thread = Thread(target=self.receive)
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


class CarRacing:
    def __init__(self,nick):
        pygame.init()
        self.display_width = 800
        self.display_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.gameDisplay = None
        self.car_x_coordinate = 360
        self.car_y_coordinate = 480
        self.availableCars = dict()
        self.availableCarsScore = dict()
        self.initialize(nick)
        self.connection = True

    def initialize(self,nick):
        self.crashed = False

        self.car1Img = pygame.image.load('.\\img\\car.png')
        self.car_width = 49

        # enemy_car
        self.enemy_car = pygame.image.load('.\\img\\enemy_car_1.png')
        self.enemy_car_startx = random.randrange(310, 450)
        self.enemy_car_starty = -600
        self.enemy_car_speed = 5
        self.enemy_car_width = 49
        self.enemy_car_height = 100

        # Background
        self.bgImg = pygame.image.load(".\\img\\back_ground.jpg")
        self.bg_x1 = (self.display_width / 2) - (360 / 2)
        self.bg_x2 = (self.display_width / 2) - (360 / 2)
        self.bg_y1 = 0
        self.bg_y2 = -600
        self.bg_speed = 3
        self.count = 0

        self.server_host = "13.51.238.1"  # Replace with the server's host address
        self.server_port = 5560  # Replace with the server's port number
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.server_host, self.server_port))
        self.nickname = nick
        self.server.send((self.nickname).encode())
        self.initialvalues = self.server.recv(1024).decode()

        self.initialvalues = self.initialvalues.split("|")
        print(self.initialvalues)
        self.car_x_coordinate, self.car_y_coordinate = self.read_pos(self.initialvalues[2])
        self.count = int(self.initialvalues[1])
        print("========================================")

    def car(self, car_x_coordinate, car_y_coordinate):
        self.gameDisplay.blit(self.car1Img, (car_x_coordinate, car_y_coordinate))

    def racing_window(self):
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Car Dodge')

        # Start a thread to receive updates from the server
        receive_thread = Thread(target=self.receive_updates)
        otherClients_thread = Thread(target=self.renderOtherClients)
        receive_thread.start()
        otherClients_thread.start()
        self.run_car()

    def renderOtherClients(self):
        print("hello from the thread")
        temp_list = []
        while True:
            left = 0
            right = 30
            if len(temp_list) == 0 and len(self.availableCars.keys()) != 0:
                newClient = Client_car()
                print("dict as list ")
                newClient.tag = list(self.availableCars.keys())[0]
                newClient.client_car = pygame.image.load('.\\img\\car2.png')
                temp_list.append(newClient)
                thingx, thingy = self.read_pos(self.availableCars[newClient.tag])
                self.gameDisplay.blit(newClient.client_car, (thingx, thingy))


            else:
                if len(self.availableCars) > len(temp_list):
                    diff = len(self.availableCars) - len(temp_list)
                    keyList = list(self.availableCars.keys())
                    for i in range(len(keyList) - diff, len(keyList)):
                        newClient = Client_car()
                        newClient.tag = keyList[i]
                        newClient.client_car = pygame.image.load('.\\img\\car2.png')
                        temp_list.append(newClient)
                font = pygame.font.SysFont("arial", 20)
                for k in temp_list:
                    thingx, thingy = self.read_pos(self.availableCars[k.tag])
                    self.gameDisplay.blit(k.client_car, (thingx, thingy))
                    text = font.render(k.tag + " Score : " + str(self.availableCarsScore[k.tag]), True, self.white)
                    self.gameDisplay.blit(text, (left, right))

                    right += 20

    def run_car(self):

        # while not self.crashed:
        while self.connection:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.connection = False
                    self.server.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.car_x_coordinate -= 50
                    if event.key == pygame.K_RIGHT:
                        self.car_x_coordinate += 50

                    # Send the updated coordinates to the server
            data = self.make_pos(self.car_x_coordinate, self.car_y_coordinate)
            msg = self.nickname + "|" + str(self.count) + "|" + data + "$"
            if self.connection:
                self.server.sendall(msg.encode())
            else:
                pygame.quit()
                exit()
                break

            if self.count >= 1000:
                self.display_message("You won, game end")
                self.connection = False
                sleep(3)
                pygame.quit()
                exit()

            self.gameDisplay.fill(self.black)
            self.back_ground_raod()
            self.car(self.car_x_coordinate, self.car_y_coordinate)  # display and update the car
            # habda

            self.run_enemy_car(self.enemy_car_startx, self.enemy_car_starty)
            self.enemy_car_starty += self.enemy_car_speed  # make care move toward my car

            if self.enemy_car_starty > self.display_height:  # i think this to create new enemy car
                self.enemy_car_starty = 0 - self.enemy_car_height
                self.enemy_car_startx = random.randrange(310, 450)  # update x co of enemy car

            # self.car(self.car_x_coordinate, self.car_y_coordinate)  # first display to the car
            self.highscore(self.count)
            self.count += 1

            if (self.count % 100 == 0):  # increase the car speen each 100 point
                self.enemy_car_speed += 1
                # self.enemy_car_speed = 0  # modify untill build 2 cares
                self.bg_speed += 1  # background speed

            if self.car_y_coordinate < self.enemy_car_starty + self.enemy_car_height:
                if self.car_x_coordinate > self.enemy_car_startx and self.car_x_coordinate < self.enemy_car_startx + self.enemy_car_width or self.car_x_coordinate + self.car_width > self.enemy_car_startx and self.car_x_coordinate + self.car_width < self.enemy_car_startx + self.enemy_car_width:
                    self.crashed = True
                    self.display_message("Game Over !!!")

            if self.car_x_coordinate < 310 or self.car_x_coordinate > 460:
                self.crashed = True
                self.display_message("Game Over !!")

            pygame.display.update()
            self.clock.tick(60)

        self.server.close()

    def back_ground_raod(self):
        self.gameDisplay.blit(self.bgImg, (self.bg_x1, self.bg_y1))  # same idea of recycle view
        self.gameDisplay.blit(self.bgImg, (self.bg_x2, self.bg_y2))

        self.bg_y1 += self.bg_speed
        self.bg_y2 += self.bg_speed

        if self.bg_y1 >= self.display_height:
            self.bg_y1 = -600

        if self.bg_y2 >= self.display_height:
            self.bg_y2 = -600

    def receive_updates(self):
        # while not self.crashed:
        while True:
            try:
                # Receive updates from the server

                data = self.server.recv(1024).decode()
                if data == "":
                    raise Exception("empty message received")

                splitted_data = data.split('$')
                for each_data in splitted_data:
                    if each_data == '':
                        splitted_data.remove(each_data)
                print(splitted_data)

                for each_data in splitted_data:
                    print("data received from server ", each_data)
                    if len(each_data.split('|')) == 3:
                        each_data = each_data.split('|')
                        carID = each_data[0]
                        score = each_data[1]
                        if int(score) >= 1000:
                            self.display_message(f"{carID} won, game end")
                            self.connection = False
                            sleep(3)
                            pygame.quit()
                            exit()

                        pos = each_data[2]
                        self.availableCarsScore[carID] = score

                        self.availableCars[carID] = pos
                    else:
                        print(each_data, " bazet hena ")
                        pos = each_data

                    print("printing the dictionary", self.availableCars)

            except Exception as e:
                # Handle server disconnection

                print(e)
                print("Disconnected from the server")
                self.connection = False
                pygame.quit()
                exit()
                break

    def display_message(self, msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        self.gameDisplay.blit(text, (400 - text.get_width() // 2, 240 - text.get_height() // 2))
        self.display_credit()
        pygame.display.update()
        self.clock.tick(60)
        sleep(1)
        # car_racing.initialize()
        # car_racing.racing_window()
        self.car_x_coordinate = 360
        self.car_y_coordinate = 480

    def run_enemy_car(self, thingx, thingy):
        self.gameDisplay.blit(self.enemy_car, (thingx, thingy))

    def display_credit(self):
        font = pygame.font.SysFont("lucidaconsole", 14)
        text = font.render("Thanks for playing!", True, self.white)
        self.gameDisplay.blit(text, (600, 520))

    def highscore(self, count):
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Score : " + str(count), True, self.white)
        self.gameDisplay.blit(text, (0, 0))

    @staticmethod
    def read_pos(data):
        data = data.split(",")
        return int(data[0]), int(data[1])

    @staticmethod
    def make_pos(x, y):
        return str(x) + "," + str(y)


class Client_car:
    def __int__(self):
        self.tag = 'tag'
        self.client_car = "imagejhdjknd"
        self.client_car_width = 49
        self.client_car_height = 100


if __name__ == '__main__':
    msg = tkinter.Tk()
    msg.withdraw()
    nickname = simpledialog.askstring("Nickname", "Please Choose a nickname", parent=msg)
    car_racing = CarRacing(nickname)
    game_thread = Thread(target=car_racing.racing_window)
    chat_client = ChatClient(nickname)
    chat_thread = Thread(target=chat_client.start_chat)
    game_thread.start()
    chat_thread.start()
