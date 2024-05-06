import socket

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Define packet size
PACKET_SIZE = 1024

# Loop to receive packets from client
while True:
    # Receive packet from client
    packet, client_address = server_socket.recvfrom(1024)

    # Simulate packet loss by dropping every other packet
    if b"ACK" not in packet:
        continue

    # Send SYN-ACK to client and wait for ACK
    if packet == b"SYN":
        server_socket.sendto(b"SYN-ACK", client_address)
        ack, _ = server_socket.recvfrom(1024)
        if ack == b"ACK":
            print("Handshake successful.")

    # Send ACK back to client for each received packet
    server_socket.sendto(b"ACK", client_address)

    # Print received packet
    print("Packet received:", packet.decode())

# Close socket
server_socket.close()
