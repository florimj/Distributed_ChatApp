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

    def discover_leader(self):
        """Listen on the discovery port for leader announcements."""
        print(f"Listening for leader-heartbeat messages on port {self.discovery_port}...")
        while True:
            response, address = self.discovery_socket.recvfrom(1024)
            data = json.loads(response.decode())
            if data["type"] == "heartbeat":
                server_id = data['id']
                if self.server_id != server_id:
                    print(f"New Leader discovered: {data['id']} at {address[0]}:{data['port']}")
                    self.server_id = server_id
                    self.server_address = (address[0], data["port"])
                    self.connect_server()
                    print("Successfully connected to leader server! \n")
        

    def connect_server(self):
        join_message={
            "type": "join",
            "id": self.id,
            "port": self.port
        }
        self.client_socket.sendto(json.dumps(join_message).encode(),self.server_address)

     def send_message(self, message):
        """Send a message to the leader server."""
        if self.server_address:
            try:
                msg = json.dumps({"type": "message", "id": self.id, "text": message})
                self.discovery_socket.sendto(msg.encode(), self.server_address)
            except Exception as e:
                print(f"Failed to send message: {e}")

    def listen_for_messages(self):
        """Listen for messages from the leader server."""
        while True:
            try:
                response, address = self.client_socket.recvfrom(1024)
                data = json.loads(response.decode())
                if data["type"] == "message":
                    print(f"Message from server: {data['text']}")
            except Exception as e:
                print(f"Error receiving message: {e}")
    



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
