import socket
import threading
import json
import uuid
import time

class ChatServer:
    def __init__(self):
        # Define Server Port and Discovery Port
        self.port = 5000 # Adjust manual for every Server
        self.discovery_port = 5010

        # Create Unique ID and Leader State
        self.id = str(uuid.uuid4())
        self.is_leader = False
        self.last_heartbeat = time.time()

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

      def broadcast_discovery(self):
        while True:
            discover_message = {
                "type": "discover",
                "id": self.id,
                "port": self.port
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

      def monitor_heartbeat(self):
        """Monitor leader's heartbeat and trigger election on failure."""
        while True:
            time.sleep(10)  # Check every 10 seconds
            if not self.is_leader and (time.time() - self.last_heartbeat > 20):  # 20-second timeout
                print("Leader unresponsive. Initiating leader election.")
                self.initiate_leader_election()

      def listen_on_discovery_port(self):
          """Listen for discovery messages on the discovery port."""
          while True:
             message, address = self.discovery_socket.recvfrom(1024)
             data = json.loads(message.decode())
             if data["type"] == "discover":
                 print(f"Discovered new server: {data['id']} at {address}")
                 self.known_servers[data["id"]] = {"ip": address[0], "port": data["port"]}
              
             print(f"Discovery message received:{message}")

      def listen_on_server_port(self):
          while True:
                 message, address = self.server_socket.recvfrom(1024)
                 print(f"Received message from {address}: {message}")

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
                        
            if data["type"] == "election":
                        print(f"Received election token {data['token']} from {address}")


      def forward_token(self, token_id):
          next_server = self.get_next_server()
          self.server_socket.sendto(json.dumps({"type": "election", "token": token_id}).encode(), next_server)

    def broadcast_message(self, message, sender):
        # Send message to all other clients
        for client in self.known_clients:
            if client != sender:  # Do not send the message back to the sender
                adress = (self.known_clients[client]["ip"],
                          self.known_clients[client]["port"])
                
      def initiate_leader_election(self):
        print(f"Server {self.id} initiating leader election.")
        # Start the election with this server's ID
        self.forward_token(self.id) 
                  
          
    
