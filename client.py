import socket

# Define server address and ports
SERVER_IP = "localhost"
SERVER_PORT = 12345

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Function to send packet with retransmission
def send_packet(packet):
    retries = 0
    while retries < NUM_RETRIES:
        # Send packet to server
        client_socket.sendto(packet, (SERVER_IP, SERVER_PORT))

        # Set timeout for receiving ACK
        client_socket.settimeout(TIMEOUT)

        try:
            # Wait for ACK from server
            ack, _ = client_socket.recvfrom(1024)

            # Check if received ACK matches packet
            if ack == b"ACK":
                print("Packet sent successfully:", packet.decode())
                return True
        except socket.timeout:
            # Handle timeout (no ACK received)
            retries += 1
            print("Timeout occurred. Retrying...")

    # If all retries are exhausted and still no ACK received, terminate
    print("Max retries reached. Exiting...")
    return False


# Handshake
client_socket.sendto(b"SYN", (SERVER_IP, SERVER_PORT))
syn_ack, _ = client_socket.recvfrom(1024)
if syn_ack == b"SYN-ACK":
    client_socket.sendto(b"ACK", (SERVER_IP, SERVER_PORT))
    print("Handshake successful.")

# Simulated data to be sent
data = b"Hello, World!"
# Define packet size
PACKET_SIZE = 1024
# Timeout for receiving ACK
TIMEOUT = 1  # in seconds
# Number of retries for packet retransmission
NUM_RETRIES = 3

# Divide data into packets
packets = [data[i:i + PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]

# Loop through each packet
for packet in packets:
    if not send_packet(packet):
        break

# Close socket
client_socket.close()