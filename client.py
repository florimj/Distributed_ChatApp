import socket
import json
import threading
import uuid

class ChatClient:
    def __init__(self, server_address):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.id = str(uuid.uuid4())

    def connect_to_server(self):
        join_message = json.dumps({"type": "join", "id": self.id})
        self.client_socket.sendto(join_message.encode(), self.server_address)
        response, _ = self.client_socket.recvfrom(1024)
        if json.loads(response.decode())["type"] == "ack":
            print("Connected to the chat server")

    def send_message(self, message):
        msg = json.dumps({"type": "message", "id": self.id, "text": message})
        self.client_socket.sendto(msg.encode(), self.server_address)

    def listen_for_messages(self):
        while True:
            response, _ = self.client_socket.recvfrom(1024)
            data = json.loads(response.decode())
            print(f"Message from {data['id']}: {data['text']}")

if __name__ == "__main__":
    client = ChatClient(('localhost', 5000))
    client.connect_to_server()
    threading.Thread(target=client.listen_for_messages).start()
    while True:
        client.send_message(input("Enter message: "))
