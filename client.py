import socket
import json
import threading
import time
import uuid

class ChatClient:
    def __init__(self, discovery_port=5010):
        # Discovery Port (UDP)
        self.discovery_port = discovery_port # Same as Server discovery_prot

        # Create UDP Socket for Discovery and Messaging with SO_REUSEADDR enabled
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.discovery_socket.bind(('', self.discovery_port))
        
        # Create Client Socket on available port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client_socket.bind(('', 0))


        # Leader Server Data
        self.server_id = None  # Current leader ID
        self.server_address = None  # Current leader address (IP, port)

        # Client ID and Port
        self.id = str(uuid.uuid4())  # Unique ID for the client
        self.port = self.client_socket.getsockname()[1]






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
