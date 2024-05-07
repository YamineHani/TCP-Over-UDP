import socket
from TCPOverUDP import send_packet, client_handshake

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Perform handshake
if not client_handshake(client_socket, SERVER_IP, SERVER_PORT):
    # Exit if handshake fails
    client_socket.close()
    exit()

# Simulated data to be sent
data = b"Hello, World!"
# Define packet size
PACKET_SIZE = 1024

# Divide data into packets
packets = [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]

# Loop through each packet
for packet in packets:
    if not send_packet(packet, SERVER_IP, SERVER_PORT, client_socket):
        break

# Close socket
client_socket.close()
