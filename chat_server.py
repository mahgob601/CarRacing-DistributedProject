import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("172.31.37.219",9999))

server.listen()
clients = []
nicknames = []

def broadcast(msg):
    for client in clients:
        client.send(msg)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{nicknames[clients.index(client)]}: {message}")
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        print(f"client's name is " + nickname)
        clients.append(client)
        nicknames.append(nickname)
        broadcast(f"{nickname} connected to the server!\n".encode('utf-8'))
        client.send("You are now connected to the server\n".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("server running")
receive()