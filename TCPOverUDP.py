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


# Handshake
def client_handshake(client_socket, SERVER_IP, SERVER_PORT):
    # Step 1: Send SYN
    client_socket.sendto(b"SYN", (SERVER_IP, SERVER_PORT))
    # Step 2: Receive SYN-ACK
    syn_ack, _ = client_socket.recvfrom(1024)
    if syn_ack == b"SYN-ACK":
        # Step 3: Send ACK
        client_socket.sendto(b"ACK", (SERVER_IP, SERVER_PORT))
        print("Handshake successful.")
        return True
    else:
        print("Handshake failed.")
        return False


def server_handshake(server_socket):
    # Receive SYN from client and send SYN-ACK
    syn_packet, client_address = server_socket.recvfrom(1024)
    if syn_packet == b"SYN":
        server_socket.sendto(b"SYN-ACK", client_address)
        print("SYN received. SYN-ACK sent.")

    # Receive ACK from client
    ack_packet, _ = server_socket.recvfrom(1024)
    if ack_packet == b"ACK":
        print("ACK received. Handshake successful.")
        return True
    else:
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