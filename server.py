import socket
import threading
import json
import uuid
from leader_election import initiate_leader_election
from heartbeat import monitor_heartbeat

class ChatServer:
    def __init__(self, port=5000):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Create UDP Socket
        self.server_socket.bind(('', self.port)) # Bind socket to port
        self.clients = {}
        self.is_leader = False
        self.id = uuid.uuid4()  # ID generieren für eindeutige Identifizierung

    def start_server(self):
        threading.Thread(target=self.listen_for_clients).start()
        threading.Thread(target=monitor_heartbeat, args=(self,)).start()
        print(f"Server running on port {self.port} and waiting for connections...")

    def listen_for_clients(self):
        while True:
            message, address = self.server_socket.recvfrom(1024)
            data = json.loads(message.decode())
            
            # Nachricht anzeigen, die vom Client empfangen wurde
            print(f"Received message from {address}: {data}")
            
            if data["type"] == "join":
                # Neuer Client hat sich verbunden
                self.clients[address] = data["id"]
                print(f"Client {data['id']} connected from {address}")
                self.server_socket.sendto(json.dumps({"type": "ack"}).encode(), address)
            elif data["type"] == "message":
                # Nachricht weiterleiten
                print(f"Received message from client {data['id']}: {data['text']}")
                self.broadcast_message(data, sender=address)

    def broadcast_message(self, message, sender):
        # Nachricht an alle anderen Clients senden
        for client in self.clients:
            if client != sender:  # Nachricht nicht an den Absender zurücksenden
                self.server_socket.sendto(json.dumps(message).encode(), client)

    def handle_leader_timeout(self):
        print("Leader not responding, initiating leader election.")
        initiate_leader_election(self)

if __name__ == "__main__":
    server = ChatServer()
    server.start_server()
