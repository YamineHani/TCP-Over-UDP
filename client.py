import socket
from TCPOverUDP import send_packet, client_handshake, generate_sequence_number, send_fin

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345
seq_number = 0
# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Perform handshake
if not client_handshake(client_socket, SERVER_IP, SERVER_PORT):
    # Exit if handshake fails
    client_socket.close()
    exit()

# Simulated data to be sent
data_packets = [
    b"Hello, World!",
    b"This is another packet.",
    b"Yet another packet.",
    # Add more data packets as needed
]

# Define packet size
PACKET_SIZE = 1024

# Loop through each data packet
for data in data_packets:
    # Divide data into packets
    packets = [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]

    # Loop through each packet
    for packet in packets:
        # Send packet with sequence number and receive ACK
        seq_number = send_packet(packet, SERVER_IP, SERVER_PORT, client_socket, seq_number)
        if seq_number is None:
            # Exit loop if sending fails
            break

# Close socket
send_fin(client_socket, SERVER_IP, SERVER_PORT, seq_number)
#client_socket.close()
