import random
import struct
import socket

# Timeout for receiving ACK
TIMEOUT = 1  # in seconds
# Define packet size
PACKET_SIZE = 1024


def calculate_checksum(data):
    checksum = 0
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)
    return ~checksum & 0xFFFF


def verify_checksum(packet_with_checksum):
    checksum = struct.unpack("!H", packet_with_checksum[:2])[0]
    data = packet_with_checksum[2:]
    calculated_checksum = calculate_checksum(data)
    return checksum == calculated_checksum


def send_packet(packet, SERVER_IP, SERVER_PORT, client_socket):
    while True:
        checksum = calculate_checksum(packet)
        # Append checksum to the packet
        packet_with_checksum = struct.pack("!H", checksum) + packet
        # Send packet to server
        client_socket.sendto(packet_with_checksum, (SERVER_IP, SERVER_PORT))
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
            print("Timeout occurred. Retrying...")


# Function to generate a random sequence number
def generate_sequence_number():
    return random.randint(1000, 9999)  # You can adjust the range as needed


# 3 way handshake:
# 1.client sends random sequence number = x
# 2. server receiver ack num = x + 1
# and generate random sequence number and send it y
# 3. client send ack number = y + 1
# and check for equalities
def client_handshake(client_socket, SERVER_IP, SERVER_PORT):
    # Step 1: Send SYN with sequence number
    seq_number = generate_sequence_number()  # x
    client_socket.sendto(f"SYN:{seq_number}".encode(), (SERVER_IP, SERVER_PORT))

    # Step 2: Receive SYN-ACK from server with server's sequence number
    syn_ack_packet, _ = client_socket.recvfrom(1024)
    if syn_ack_packet.startswith(b"SYN-ACK"):
        syn_ack_info = syn_ack_packet.decode().split(":")[1:]
        server_seq_number = int(syn_ack_info[0]) # y
        server_ack_number = int(syn_ack_info[1]) # x + 1

        if server_ack_number == seq_number + 1:
            # Step 3: Send ACK with client's sequence and acknowledgment numbers
            client_socket.sendto(f"ACK:{server_seq_number + 1}".encode(), (SERVER_IP, SERVER_PORT))
            print("Handshake successful.")
            return True
    print("Handshake failed.")
    return False


def server_handshake(server_socket):
    # Step 1: Receive SYN from client with client's sequence number
    syn_packet, client_address = server_socket.recvfrom(1024)
    if syn_packet.startswith(b"SYN"):
        client_seq_number = int(syn_packet.decode().split(":")[1])  # x

        # Step 2: Send SYN-ACK to client with server's sequence and acknowledgment numbers
        server_seq_number = generate_sequence_number()  # y
        server_ack_number = client_seq_number + 1
        syn_ack_packet = f"SYN-ACK:{server_seq_number}:{server_ack_number}".encode()
        server_socket.sendto(syn_ack_packet, client_address)
        print("SYN received. SYN-ACK sent.")

        # Step 3: Receive ACK from client with acknowledgment number = y + 1
        ack_packet, _ = server_socket.recvfrom(1024)
        if ack_packet.startswith(b"ACK"):
            ack_info = ack_packet.decode().split(":")[1]
            client_ack_number = int(ack_info)
            if client_ack_number == server_seq_number + 1:
                print("ACK received. Handshake successful.")
                return True
    print("Handshake failed.")
    return False


def receive_packets(server_socket):
    while True:
        # Receive packet from client
        packet_with_checksum, client_address = server_socket.recvfrom(1024)

        # Verify checksum
        if verify_checksum(packet_with_checksum):
            packet = packet_with_checksum[2:]
            # Print received packet
            print("Packet received:", packet.decode())

            # Send ACK back to client for each received packet
            server_socket.sendto(b"ACK", client_address)
        else:
            print("Checksum verification failed. Packet dropped.")
