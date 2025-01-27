import socket
import threading
import json
import uuid
import time

class ChatServer:
    def __init__(self):
        # Define Server Port and Discovery Port
        self.port = 5000 # Adjust manually for every Server
        self.discovery_port = 5010

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
             server_id = data['id']
             server_ip = address[0]
            
             if data["type"] == "discover":
                if server_id not in self.known_servers:
                    server_ip = server_ip
                    server_port = data ['port']
                    self.known_servers[server_id] = {
                        "id": server_id,
                        "ip": server_ip,
                        "port": server_port,
                        "isLeader": data['isLeader']
                    }
                    print(f"Discovered new server: {server_ip}:{server_port}")
            elif data["type"] == "leader":
                leader_id = server_id
                server_port = data ['port']
                print(f"Server {leader_id} has been elected as leader.")

                #update status
                self.is_leader = (leader_id == self.id)
                self.voted = False
                
                # Update the respective server entry with `isLeader=True`
                if leader_id in self.known_servers:
                    self.known_servers[leader_id]["isLeader"] = True

                else:
                    print(f"Leader {leader_id} not found in known servers. Adding it.")
                    # Add leader to the known_servers if not already present
                    self.known_servers[leader_id] = {
                        "id": leader_id,
                        "ip": address[0],
                        "port": server_port,
                        "isLeader": True
                    }

            elif data["type"] == "heartbeat":
                    leader_id = server_id
                    if leader_id == self.id: # Ignore heartbeats from self
                        return  
                    print(f"Heartbeat received from leader {server_ip}:{server_port}.")
                    self.last_heartbeat = time.time()  # Update the last heartbeat timestamp


    def forward_token(self, token_id):
        """Send the election token to the next server in the logical ring."""
        sorted_servers = sorted(self.known_servers.values(), key=lambda x: x["id"])
        my_index = next((i for i, server in enumerate(sorted_servers) if server["id"] == self.id), None)

        if my_index is None:
            print("Error: This server is not in the known_servers list.")
            return

        # Find the next server in the ring
        next_server = sorted_servers[(my_index + 1) % len(sorted_servers)]
        next_address = (next_server["ip"], next_server["port"])

        try:
            print(f"Forwarding token {token_id} to {next_server['id']} at {next_address}.")
            self.server_socket.sendto(json.dumps({"type": "election", "token": token_id}).encode(), next_address)
        
        except:
            print(f"Failed to send token {token_id} to {next_server['id']} at {next_address}")
            print(f"Removing server {next_server['id']} from known servers due to failure.")
            self.known_servers.pop(next_server["id"], None)  # Remove the unreachable server


    def broadcast_leader(self):
        """Broadcast leader information to all known servers."""
        for server in self.known_servers.values():
            leader_message = {
                "type": "leader",
                "id": self.id,
                "port":self.port
            }
            print(f"Leader {self.id} will be broadcasted to all known servers.")
            self.discovery_socket.sendto(json.dumps(leader_message).encode(), ('<broadcast>', self.discovery_port))
        

      def listen_on_server_port(self):
          while True:
              try:
                  message, address = self.server_socket.recvfrom(1024)
                  #print(message)
                  data = json.loads(message.decode())

                  # Display message received from the client
                  #print(f"Received message from {address}: {data}")
    
                  if data["type"] == "join":
                    # New client connected
                    client_id = data["id"]
                    client_ip = address[0]
                    client_port= data["port"]

                    if client_id not in self.known_clients:
                        self.known_clients[client_id] = {
                            "id": client_id,
                            "ip": client_ip,
                            "port": client_port,
                        }

                    print(f"Client {data['id']} connected from {address}")

                  elif data["type"] == "message":
                    # Forward message
                    print(f"Received message from client {data['id']}: {data['text']}")
                    self.broadcast_message(data, data['id'])
                  
                  elif data["type"] == "election":
                    token_id = data["token"]
                    print(f"Received election token {token_id} from {address}.")
                    if (self.voted==False):
                        if token_id > self.id:
                            # Forward the token unchanged
                                self.forward_token(token_id)
                        elif token_id < self.id:
                            # Replace with this server's ID and forward
                            self.forward_token(self.id)
                        elif token_id == self.id:
                            # This server is the leader
                            print(f"I have won the election!")
                            self.is_leader = True
                            self.broadcast_leader()
                            threading.Thread(target=self.broadcast_heartbeat).start()
                    else:
                        print("I already voted and my own token is the highest. I am the leader now!")
                        self.broadcast_leader()   
                        threading.Thread(target=self.broadcast_heartbeat).start()
                self.voted = True
                
              except Exception as e:
                print("Someone disconnected!")
                print(e)
                
                # Find the next server in the ring
                sorted_servers = sorted(self.known_servers.values(), key=lambda x: x["id"])
                my_index = next((i for i, server in enumerate(sorted_servers) if server["id"] == self.id), None)
                next_server = sorted_servers[(my_index + 1) % len(sorted_servers)]
                next_address = (next_server["ip"], next_server["port"])
                print(f"Remove {next_address} from known servers list")
                self.known_servers.pop(next_server["id"], None)  # Remove the unreachable server

    
    def broadcast_message(self, message, sender):
        # Send message to all other clients
        for client in self.known_clients:
            if client != sender:  # Do not send the message back to the sender
                adress = (self.known_clients[client]["ip"],
                          self.known_clients[client]["port"])
                try:
                    self.server_socket.sendto(json.dumps(message).encode(), adress)
                except Exception as e:
                    print(e)
                    
      def initiate_leader_election(self):
        print(f"Server {self.id} initiating leader election.")
        # Start the election with this server's ID
        self.forward_token(self.id) 


if __name__ == "__main__":
    server = ChatServer()
    server.start_server()                  
          
    
