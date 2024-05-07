import socket
from TCPOverUDP import server_handshake, receive_packets

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))


try:
    if server_handshake(server_socket):
        receive_packets(server_socket)
finally:
    # Close socket
    server_socket.close()
