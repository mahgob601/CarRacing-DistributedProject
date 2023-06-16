import socket
import threading

class Server:
    def __init__(self):
        self.host = "localhost"
        self.port = 5560
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.clients = []
        self.cars = []

    def handle_client(self, client, car,address):
        while True:
            try:
                print("in try in client handle")
                # Receive the updated coordinates from the client
                data = client.recv(1024).decode()
                print(data)
                print("check1")
                car_x, car_y = self.read_pos(data)# throw an exception here bc data is empty
                print("check2")
                car.car_x_coordinate = car_x
                car.car_y_coordinate = car_y
                #print("check3")
                # Broadcast the updated coordinates to all clients
                for c in self.clients:
                    if c != client:
                        myData = str(address) + "|" + data
                        c.sendall(myData.encode())
                    else:
                        print("check4")
            except:
                # Handle client disconnection
                print("in exception in client handle")
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
            #client.sendall("Welcome to the game!".encode())

            # Create a new car for the client
            car = Car()
            self.cars.append(car)

            # Send the initial car coordinates to the client
            client.sendall(self.make_pos(car.car_x_coordinate, car.car_y_coordinate).encode())

            # Start a new thread to handle the client
            thread = threading.Thread(target=self.handle_client, args=(client, car,address))
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
        self.car_x_coordinate = 360
        self.car_y_coordinate = 480

if __name__ == "__main__":
    server = Server()
    server.start()
