import socket

def discover_hosts(port=5000):
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    discovery_socket.sendto(b"DISCOVER", ('<broadcast>', port))
