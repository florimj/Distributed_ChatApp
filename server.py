import socket
import threading
import json
import uuid
import time

class ChatServer:
    def __init__(self):
        # Define Server Port and Discovery Port
        self.port = 5000 # Adjust manually
        self.discovery_port = 5010 # Same as Client discovery_prot
    
        # Create Unique ID and Leader State
        self.id = str(uuid.uuid4())
        self.is_leader = False
        self.last_heartbeat = time.time()
        self.voted = False  

        # Server Socket Initialization
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP Socket
        self.server_socket.bind(('', self.port))  # Bind socket to port
        self.ip = socket.gethostbyname(socket.gethostname())

        # Discovery Socket Initialization
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP Socket
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Enable address reuse
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        self.discovery_socket.bind(('', self.discovery_port))  # Bind to discovery port

        # Client and Server List
        self.known_clients = {}  # Store connected clients
        self.known_servers = {}  # Store discovered servers

    def start_server(self):
        print("------------------------------------------")
        print(f"Server IP: {self.ip} Server ID: {self.id}")
        print("------------------------------------------")
        print(f"Server running on port {self.port} and waiting for connections ...")
        print(f"Listening for discovery messages on port {self.discovery_port} ...")

        threading.Thread(target=self.listen_on_server_port).start()
        threading.Thread(target=self.listen_on_discovery_port).start()
        threading.Thread(target=self.monitor_heartbeat).start()
        threading.Thread(target=self.broadcast_discovery).start()

        # Delay election to allow discovery
        time.sleep(10)
        print("Initiating leader election at startup...")
        self.initiate_leader_election()

    def broadcast_discovery(self):
        while True:
            discover_message = {
                "type": "discover",
                "id": self.id,
                "port": self.port,
                "isLeader": self.is_leader
            }
            self.discovery_socket.sendto(json.dumps(discover_message).encode(),
                                         ('<broadcast>', self.discovery_port))
            print(f"Broadcasting discovery message from {self.id}")
            time.sleep(10)  # Send discovery messages every 10 seconds

    def broadcast_heartbeat(self):
        """Leader periodically sends heartbeat messages to all servers."""
        while self.is_leader:
            heartbeat_message = {
                "type": "heartbeat",
                "id": self.id,
                "port": self.port
            }
            self.discovery_socket.sendto(json.dumps(heartbeat_message).encode(), ('<broadcast>', self.discovery_port))
            print("Heartbeat sent by the leader.")
            time.sleep(10)  # Heartbeat interval




# Aus Vorlesung:
    # Server:
       # import socket
       # Server in Python
       # # Create a UDP socket
       # server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # # Server application IP address and port
       # server_address = '127.0.0.1'
       # server_port = 10001
       # # Buffer size
       # buffer_size = 1024
       # message = 'Hi client! Nice to connect with you!’
       # # Bind socket to port
       # server_socket.bind((server_address, server_port))
       # print('Server up and running at {}:{}'.format(server_address, server_port))
       # while True:
       # print('\nWaiting to receive message...\n')
       # data, address = server_socket.recvfrom(buffer_size)
       # print('Received message from client: ', address)
       # print('Message: ', data.decode())
       # if data:
       # server_socket.sendto(str.encode(message), address)
       # print('Replied to client: ', message)


    # Broadcast sender:
       # def broadcast(ip, port, broadcast_message):
       # # Create a UDP socket
       # broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       # # Send message on broadcast address
       # broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
       # if __name__ == '__main__':
       # # Broadcast address and port
       # BROADCAST_IP = "192.168.0.255"
       # BROADCAST_PORT = 5973
       # # Local host information
       # MY_HOST = socket.gethostname()
       # MY_IP = socket.gethostbyname(MY_HOST)
       # # Send broadcast message
       # message = MY_IP + ' sent a broadcast message'
       # broadcast(BROADCAST_IP, BROADCAST_PORT, message)
