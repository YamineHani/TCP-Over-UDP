import socket

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Define packet size
PACKET_SIZE = 1024

# Receive SYN from client and send SYN-ACK
syn_packet, client_address = server_socket.recvfrom(1024)
if syn_packet == b"SYN":
    server_socket.sendto(b"SYN-ACK", client_address)
    print("SYN received. SYN-ACK sent.")

# Receive ACK from client
ack_packet, _ = server_socket.recvfrom(1024)
if ack_packet == b"ACK":
    print("ACK received. Handshake successful.")

# Loop to receive packets from client
while True:
    # Receive packet from client
    packet, _ = server_socket.recvfrom(1024)

    # Print received packet
    print("Packet received:", packet.decode())

    # Send ACK back to client for each received packet
    server_socket.sendto(b"ACK", client_address)

# Close socket
server_socket.close()