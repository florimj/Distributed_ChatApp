import socket
import threading
import json
import uuid

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
