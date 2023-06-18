import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("172.31.27.158", 5561))

server.listen()
clients = []
nicknames = []


def handle_backup():
    main_server, address = server.accept()
    main_server.settimeout(3)
    while True:
        try:
            backup = main_server.recv(1024).decode('utf-8')
            if backup != "":
                print(backup)
            else:
                print("back up message is empty")
                raise Exception

        except:
            print("server crashed")
            try:
                main_server.close()
                receive()
            except:
                print("something happened while launching the backup server")
                break

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
        connected_clients = "NEWCONN"
        clients.append(client)
        nicknames.append(nickname)
        for i in nicknames:
            connected_clients = connected_clients + " " + i
        print(connected_clients)
        connected_clients = connected_clients + "$"
        broadcast(connected_clients.encode('utf-8'))

        broadcast(f"CHAT {nickname} connected to the server!\n$".encode('utf-8'))
        client.send("CHAT You are now connected to the server\n$".encode('utf-8'))
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("server running")
handle_backup()
