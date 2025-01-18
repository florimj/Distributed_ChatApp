import socket
import json
import threading
import uuid

class ChatClient:
    def __init__(self, server_address):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create UDP Socket
        self.server_address = server_address # Bind socket to port
        self.id = str(uuid.uuid4()) # ID generieren für eindeutige Identifizierung

    def connect_to_server(self):
        join_message = json.dumps({"type": "join", "id": self.id})
        self.client_socket.sendto(join_message.encode(), self.server_address)
        response, _ = self.client_socket.recvfrom(1024)
        if json.loads(response.decode())["type"] == "ack":
            print("Connected to the chat server")

    def send_message(self, message):
        msg = json.dumps({"type": "message", "id": self.id, "text": message})
        self.client_socket.sendto(msg.encode(), self.server_address)

    def listen_for_messages(self):
        while True:
            response, _ = self.client_socket.recvfrom(1024)
            data = json.loads(response.decode())
            if data["type"] == "message":
                print(f"Message from another client: {data['text']}")


if __name__ == "__main__":
    client = ChatClient(('localhost', 5000))
    client.connect_to_server()
    threading.Thread(target=client.listen_for_messages).start()
    while True:
        client.send_message(input("Enter message: "))


# Aus Vorlseung:
    # Client
       # import socket
       # # Create a UDP socket
       # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # # Bind the socket to the port
       # server_address = '127.0.0.1'
       # server_port = 10001
       # # Buffer size
       # buffer_size = 4096
       # message = 'Hi server!'
       # # Send data
       # client_socket.sendto(message.encode(), (server_address, server_port))
       # print('Sent to server: ', message)
       # # Receive response
       # print('Waiting for response...')
       # data, server = client_socket.recvfrom(buffer_size)
    # print('Received message from server: ', data.decode())

     # For TCP sockets
       # try:
       # # Send data
       # …
       # # Receive response
       # …
       # finally:
       # client_socket.close()
       # print('Socket closed')


    # Broadcast sender:
         # Listening port
           # BROADCAST_PORT = 5972
           # # Local host information
           # MY_HOST = socket.gethostname()
           # MY_IP = socket.gethostbyname(MY_HOST)
           # # Create a UDP socket
           # listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
           # # Set the socket to broadcast and enable reusing addresses
           # listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
           # listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
           # # Bind socket to address and port
           # listen_socket.bind((MY_IP, BROADCAST_PORT))
           # print("Listening to broadcast messages")
           # while True:
           # data, addr = listen_socket.recvfrom(1024)
           # if data:
           # print("Received broadcast message:", data.decode())
