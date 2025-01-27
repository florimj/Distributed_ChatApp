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
                    
if __name__ == "__main__":
    client = ChatClient(discovery_port=5010)

    # Discover the leader
    threading.Thread(target=client.discover_leader, daemon=True).start()

    # Start listening for messages from the server
    threading.Thread(target=client.listen_for_messages, daemon=True).start()

    # Send messages to the server
    while True:
        while(client.server_id != None):
            message = input("\n Enter message: ")
            client.send_message(message)
