import socket

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Function to send packet without retransmission
def send_packet(packet):
    # Send packet to server
    client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))

    # Wait for ACK from server
    ack, _ = client_socket.recvfrom(1024)

    # Check if received ACK matches packet
    if ack != b"ACK":
        print("Packet not acknowledged:", packet.decode())


# Simulated data to be sent
data = b"Hello, World!"

# Define packet size
PACKET_SIZE = 1024

# Divide data into packets
packets = [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]

# Handshake
client_socket.sendto(b"SYN", (SERVER_IP, SERVER_PORT))
syn_ack, _ = client_socket.recvfrom(1024)
if syn_ack == b"SYN-ACK":
    client_socket.sendto(b"ACK", (SERVER_IP, SERVER_PORT))
    print("Handshake successful.")

# Loop through each packet
for packet in packets:
    send_packet(packet)

# Close socket
client_socket.close()

