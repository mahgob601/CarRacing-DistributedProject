import socket
import threading
#main server
class Server:
    def __init__(self):
        self.host = "172.31.27.158"
        self.port = 5560
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.cars = []
        self.serveravailable=dict()
        self.serverscore=dict()
        self.myScore = 0
        self.max = 0

    def handle_client(self, client, car,address):
        while True:
            try:
                #score ==> 1 coor ==> 2 ID ==> 0
                print("in try in client handle")
                # Receive the updated coordinates from the client
                data = client.recv(1024).decode()
                if data == "":
                    raise Exception("empty message spam")

                splitted_data = data.split('$')
                for each_data in splitted_data:
                    if each_data == '':
                        splitted_data.remove(each_data)

                print(data)
                print(splitted_data)
                print("check1")
                for each_data in splitted_data:
                    coords = each_data.split("|")[2]
                    car_x, car_y = self.read_pos(coords)# throw an exception here bc data is empty
                    print("check2")
                    car.car_x_coordinate = car_x
                    car.car_y_coordinate = car_y
                    print("check3")
                    # Broadcast the updated coordinates to all clients
                    self.serveravailable[address]= coords
                    self.serverscore[address]= int(each_data.split("|")[1])
                    print(self.serveravailable)
                    print(self.serverscore)

                    for c in self.clients:
                        if c != client:
                            #myData = str(address) + "|" + data
                            myData = each_data + "$"
                            c.sendall(myData.encode())
                        else:
                            print("check4")

            except Exception as e:
                # Handle client disconnection
                print("in exception in client handle")
                print(e)
                index = self.clients.index(client)
                self.clients.remove(client)
                car = self.cars[index]
                self.cars.remove(car)
                client.close()
                break

    def start(self):
        print("Server started. Waiting for connections...")
        while True:
            client, address = self.server.accept()
            print("Connected to:", address)
            print("Connected to:", client)
            nickname= client.recv(1024).decode()
            print(f"{nickname} ba2a connected")
            #client.sendall("Welcome to the game!".encode())
            if nickname not in self.serveravailable:
                # Create a new car for the client
                car = Car()
                self.cars.append(car)
                self.myScore = 0
            else:
                data= self.serveravailable[nickname]
                self.myScore = self.serverscore[nickname]
                coords = data
                car_x, car_y = self.read_pos(coords)
                car = Car()
                self.cars.append(car)
                car.car_x_coordinate=car_x
                car.car_y_coordinate=car_y

            # Send the initial car coordinates to the client
            coordStr = self.make_pos(car.car_x_coordinate, car.car_y_coordinate)
            toBeSent = str(nickname) + "|" + str(self.myScore) + "|"+ coordStr
            #client.sendall(self.make_pos(car.car_x_coordinate, car.car_y_coordinate).encode())
            client.sendall(toBeSent.encode())
            # Start a new thread to handle the client
            thread = threading.Thread(target=self.handle_client, args=(client, car,nickname))
            thread.start()

            self.clients.append(client)
            print(f"Active connections: {len(self.clients)}")

    @staticmethod
    def read_pos(data):
        data = data.split(",")
        #print("check in read_pos")
        return int(data[0]), int(data[1])

    @staticmethod
    def make_pos(x, y):
        return str(x) + "," + str(y)


class Car:
    def __init__(self):
        self.car_x_coordinate = 310
        self.car_y_coordinate = 480

if __name__ == "__main__":
    server = Server()
    server.start()
