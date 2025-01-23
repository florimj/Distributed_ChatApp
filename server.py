import socket
import threading
import json
import uuid
import time

class ChatServer:
    def __init__(self):
        # Define Server Port and Discovery Port
        self.port = 5003
        self.discovery_port = 5010

        # Create Unique ID and Leader State
        self.id = str(uuid.uuid4())
        self.is_leader = False


        # Server Socket Initialization
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP Socket
        self.server_socket.bind(('', self.port))  # Bind socket to port
        self.ip = socket.gethostbyname(socket.gethostname())

        # Discovery Socket Initialization
        self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP Socket
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Enable address reuse
        self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        self.discovery_socket.bind(('', self.discovery_port))  # Bind to discovery port
      
      def start_server(self):
        print("------------------------------------------")
        print(f"Server IP: {self.ip} Server ID: {self.id}")
        print("------------------------------------------")
        print(f"Server running on port {self.port} and waiting for connections ...")
        print(f"Listening for discovery messages on port {self.discovery_port} ...")

        threading.Thread(target=self.listen_on_server_port).start()
        threading.Thread(target=self.listen_on_discovery_port).start()

      def listen_on_discovery_port(self):
         """Listen for discovery messages on the discovery port."""
         while True:
             message, address = self.discovery_socket.recvfrom(1024)
           print(f"Discovered new server: {server_ip}:{server_port}")

     def listen_on_server_port(self):
            while True:
                    message, address = self.server_socket.recvfrom(1024)
                  print(f"Client {data['id']} connected from {address}")

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

    def listen_on_discovery_port(self):
        """Listen for discovery messages on the discovery port."""
        while True:
            message, address = self.discovery_socket.recvfrom(1024)
            data = json.loads(message.decode())
            server_id = data['id']
            server_ip = address[0]
            
            if data["type"] == "discover":
                print(f"Discovered new server: {server_ip}:{server_port}")
                    self.known_servers[server_id] = {
                        "id": server_id,
                        "ip": server_ip,
                        "port": server_port,
                        "isLeader": data['isLeader']
                  
          
    
