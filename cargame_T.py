import random
import pygame
from time import sleep
import socket
from threading import Thread
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog


class CarRacing:
    def __init__(self):
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
        self.initialize()

    def initialize(self):
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

        self.server_host = "localhost"  # Replace with the server's host address
        self.server_port = 5560  # Replace with the server's port number
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.server_host, self.server_port))
        self.nickname=self.client_Nickname()
        self.server.send((self.nickname).encode())

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
        temp_list=[]
        while True:
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
                for k in temp_list:
                    thingx, thingy = self.read_pos(self.availableCars[k.tag])
                    self.gameDisplay.blit(k.client_car, (thingx, thingy))







    def run_car(self):

        #while not self.crashed:
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.crashed = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.car_x_coordinate -= 50
                    if event.key == pygame.K_RIGHT:
                        self.car_x_coordinate += 50

                    # Send the updated coordinates to the server
                    data = self.make_pos(self.car_x_coordinate, self.car_y_coordinate)
                    self.server.sendall(data.encode())

            self.gameDisplay.fill(self.black)
            self.back_ground_raod()
            self.car(self.car_x_coordinate, self.car_y_coordinate)#display and update the car
            # habda


            self.run_enemy_car(self.enemy_car_startx, self.enemy_car_starty)
            self.enemy_car_starty += self.enemy_car_speed  # make care move toward my car

            if self.enemy_car_starty > self.display_height:  # i think this to create new enemy car
                self.enemy_car_starty = 0 - self.enemy_car_height
                self.enemy_car_startx = random.randrange(310, 450)  # update x co of enemy car

            #self.car(self.car_x_coordinate, self.car_y_coordinate)  # first display to the car
            self.highscore(self.count)
            self.count += 1

            if (self.count % 100 == 0):  # increase the car speen each 100 point
                #self.enemy_car_speed += 1
                self.enemy_car_speed = 0  # modify untill build 2 cares
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
        #while not self.crashed:
        while True:
            try:
                # Receive updates from the server

                data = self.server.recv(1024).decode()
                print("data received from server " , data)
                if len(data.split('|'))>1:
                    data = data.split('|')
                    carID = data[0]

                    pos = data[1]
                    self.availableCars[carID]=pos
                else:
                    pos = data

                print("printing the dictionary",self.availableCars)
                #car_x, car_y = self.read_pos(pos)
                #self.car_x_coordinate = car_x
                #self.car_y_coordinate = car_y
            except:
                # Handle server disconnection

                self.crashed = True
                print("Disconnected from the server")

    def display_message(self, msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        self.gameDisplay.blit(text, (400 - text.get_width() // 2, 240 - text.get_height() // 2))
        self.display_credit()
        pygame.display.update()
        self.clock.tick(60)
        sleep(1)
        #car_racing.initialize()
        #car_racing.racing_window()
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
    def client_Nickname(self):
        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please Choose a nickname", parent=msg)
        print(self.nickname)
        return self.nickname
class Client_car:
    def __int__(self):
        self.tag= 'tag'
        self.client_car ="imagejhdjknd"
        self.client_car_width = 49
        self.client_car_height = 100

if __name__ == '__main__':
    car_racing = CarRacing()
    car_racing.racing_window()