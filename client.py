import socket
import json
import threading
import time
import uuid

class ChatClient:
    def __init__(self, discovery_port=5010):
        # Discovery Port (UDP)
        self.discovery_port = discovery_port

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
