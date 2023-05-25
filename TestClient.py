import socket

def test_client():
    server_host = "localhost" # Update with the server's host address
    server_port = 5560  # Update with the server's port number

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the server
        client_socket.connect((server_host, server_port))
        print("Connected to the server!")

        # Send a test message to the server
        message = "Test message from client"
        client_socket.send(message.encode())

        # Receive a response from the server
        response = client_socket.recv(1024).decode()
        print("Received response from the server:", response)

    except ConnectionRefusedError:
        print("Connection to the server was refused.")

    finally:
        # Close the socket
        client_socket.close()

# Call the test_client function to initiate the connection test
test_client()
