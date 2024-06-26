import random
import struct
import socket

from database import handle_get_request, handle_post_request

# Timeout for receiving ACK
TIMEOUT = 1  # in seconds
# Define packet size
PACKET_SIZE = 1024
# Define packet loss and corruption probabilities
PACKET_LOSS_PROBABILITY = 0.02  # 2% packet loss
PACKET_CORRUPTION_PROBABILITY = 0.1  # 10% corruption


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


# Function to generate a random sequence number
def generate_sequence_number():
    return random.randint(0, 255)  # You can adjust the range as needed


# 3 way handshake:
# 1.client sends random sequence number = x
# 2. server receiver ack num = x + 1
# and generate random sequence number and send it y
# 3. client send ack number = y + 1
# and check for equalities
# TODO: ADD TIMEOUT IN HANDSHAKE TO HANDLE PACKET LOSS
def client_handshake(client_socket, server_ip, server_port):
    while True:
        # Step 1: Send SYN with sequence number
        seq_number = generate_sequence_number()  # x
        client_socket.sendto(f"SYN:{seq_number}".encode(), (server_ip, server_port))
        # Set timeout for receiving SYN-ACK packet
        client_socket.settimeout(TIMEOUT)

        try:
            # Step 2: Receive SYN-ACK from server with server's sequence number
            syn_ack_packet, _ = client_socket.recvfrom(1024)
            if syn_ack_packet.startswith(b"SYN-ACK"):
                syn_ack_info = syn_ack_packet.decode().split(":")[1:]
                server_seq_number = int(syn_ack_info[0])  # y
                server_ack_number = int(syn_ack_info[1])  # x + 1

                if server_ack_number == seq_number + 1:
                    # Step 3: Send ACK with client's sequence and acknowledgment numbers
                    client_socket.sendto(f"ACK:{server_seq_number + 1}".encode(), (server_ip, server_port))
                    print("Handshake successful.")
                    return True
        except socket.timeout:
            print("Timeout occurred while waiting for SYN-ACK.")
            client_socket.sendto(f"SYN:{seq_number}".encode(), (server_ip, server_port))


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


# Use 2 sequence numbers 1 and 0:
# 1. Sender start by sending packet with sequence number 0
# 2. Sender waits for ACK0 from receiver
# 3. If ACK1 received instead of ACK0 || packet corrupted just wait for timeout and resend packet
# 4. If ACK0 received, send next packet with sequence number 1
# 5. Repeat
def send_packet(packet, server_ip, server_port, client_socket, seq_number):
    while True:
        if packet.startswith(b"GET"):
            id = ''.join(packet.split(b' ')[1].decode())
            packet = get_request(id)
        elif packet.startswith(b"POST"):
            unpack_post = packet.split(b' ')[1:]
            name = ' '.join(item.decode() for item in unpack_post)
            packet = post_request(name)

        # Append sequence number to the packet
        packet_with_seq_num = struct.pack("!B", seq_number) + packet
        # Calculate checksum on the entire packet
        checksum = calculate_checksum(packet_with_seq_num)
        # Append checksum to the packet
        packet_with_metadata = struct.pack("!H", checksum) + packet_with_seq_num
        # Send packet to server
        client_socket.sendto(packet_with_metadata, (server_ip, server_port))
        # Set timeout for receiving ACK
        client_socket.settimeout(TIMEOUT)
        try:
            # Wait for ACK from server
            ack_packet_with_checksum, _ = client_socket.recvfrom(1024)
            # Verify checksum of the ACK packet
            ack_checksum = struct.unpack("!H", ack_packet_with_checksum[:2])[0]
            ack_packet = ack_packet_with_checksum[2:]
            if calculate_checksum(ack_packet) == ack_checksum:
                # Extract sequence number from ACK packet
                ack_seq_number = struct.unpack("!B", ack_packet[:1])[0]
                print("ack number: ", ack_seq_number)
                # Check if received ACK matches the sequence number of the sent packet
                if ack_seq_number == seq_number:
                    print("Packet sent successfully:", packet.decode())

                    response_content = ack_packet[1:]
                    if len(response_content) != 0:
                        print("Response from server:", response_content.decode())

                    # Toggle sequence number for next packet
                    return 1 - seq_number
        except socket.timeout:
            # Handle timeout (no ACK received)
            print("Timeout occurred. Retrying...")


def receive_packets(server_socket, expected_seq_number):
    while True:
        if lose_packet():
            print("Packet lost.")
        else:
            # Receive packet from client
            packet_with_metadata, client_address = server_socket.recvfrom(1024)

            # Check if the packet is a FIN packet
            packet = packet_with_metadata[1:]
            fin_seq_number = packet_with_metadata[:1][0]
            if packet == b"FIN":
                print("Received FIN packet from client with sequence: ", fin_seq_number)
                # Process the FIN packet (e.g., initiate connection termination)
                handle_fin(server_socket, fin_seq_number, client_address)
                return  # Exit the loop after handling the FIN packet

            if corrupt_packet():
                # Corrupt a random byte in the packet
                index = random.randint(0, len(packet_with_metadata) - 1)
                packet_with_metadata = packet_with_metadata[:index] + bytes(
                    [random.randint(0, 255)]) + packet_with_metadata[index + 1:]
                print("Packet corrupted.")

            # Extract sequence number from received packet
            recv_seq_number = struct.unpack("!B", packet_with_metadata[2:3])[0]

            # Verify checksum
            if verify_checksum(packet_with_metadata):
                # Check if received packet is the expected packet
                if recv_seq_number == expected_seq_number:
                    packet = packet_with_metadata[3:]
                    # Print received packet
                    print("received seq num: ", recv_seq_number)
                    print("Packet received:", packet.decode())

                    # Send ACK back to client along with the sequence number
                    ack_packet = struct.pack("!B", recv_seq_number)

                    # Check if packet is HTTP request
                    if packet.startswith(b"GET"):
                        response = handle_get_request(packet)
                        ack_packet += response
                    elif packet.startswith(b"POST"):
                        response = handle_post_request(packet)
                        ack_packet += response

                    # Calculate checksum for ACK packet
                    ack_checksum = calculate_checksum(ack_packet)
                    # Append checksum to the ACK packet
                    ack_packet_with_checksum = struct.pack("!H", ack_checksum) + ack_packet
                    # Send ACK back to client for each received packet
                    server_socket.sendto(ack_packet_with_checksum, client_address)
                    # Toggle expected sequence number for next packet
                    expected_seq_number = 1 - expected_seq_number
                else:
                    # Duplicate packet or out-of-order packet, discard and request retransmission
                    print("Out-of-order or duplicate packet received. Discarding...")
            else:
                # Checksum verification failed, request retransmission
                print("Checksum verification failed. Packet dropped. Requesting retransmission...")


def lose_packet():
    return random.random() < PACKET_LOSS_PROBABILITY


def corrupt_packet():
    return random.random() < PACKET_CORRUPTION_PROBABILITY


# 1. client sends FIN and seq number = x
# 2. server replies with ack and ack number = x+1
# 3. then server sends FIN and seq num = y
# 4. clients replies with ACK and ack number = y+1
# 5. and both closes connection
def send_fin(client_socket, server_ip, server_port, seq_number):
    # Send FIN segment with sequence number
    fin_packet = struct.pack("!B", seq_number) + b"FIN"
    client_socket.sendto(fin_packet, (server_ip, server_port))
    print("Client: FIN sent to server with sequence number:", seq_number)

    # Wait for ACK from server
    while True:
        try:
            client_socket.settimeout(TIMEOUT)
            acknowledgment, _ = client_socket.recvfrom(1024)
            ack_seq_number = struct.unpack("!B", acknowledgment[:1])[0]
            if acknowledgment[1:] == b"ACK" and ack_seq_number == seq_number + 1:
                print("Client: ACK received from server for FIN with sequence number:", ack_seq_number)
                break
        except socket.timeout:
            print("Client: Timeout occurred while waiting for ACK from server. Retrying...")
            client_socket.sendto(fin_packet, (server_ip, server_port))
            print("Client: FIN sent to server with sequence number:", seq_number)

    # Wait for FIN from server
    while True:
        fin_packet, _ = client_socket.recvfrom(1024)
        server_seq_number = struct.unpack("!B", fin_packet[:1])[0]
        if fin_packet[1:] == b"FIN":
            print("Client: FIN received from server with sequence number:", server_seq_number)

            # Send ACK to acknowledge FIN from server
            ack_packet = struct.pack("!B", server_seq_number + 1) + b"ACK"
            client_socket.sendto(ack_packet, (server_ip, server_port))
            print("Client: ACK sent to server for FIN with sequence number:", server_seq_number + 1)
            break

    # Close socket
    client_socket.close()


def handle_fin(server_socket, seq_number, client_address):
    # Send ACK with acknowledgment number = sequence number + 1
    ack_packet = struct.pack("!B", seq_number + 1) + b"ACK"
    server_socket.sendto(ack_packet, client_address)
    print("Server: ACK sent to client with acknowledgment number:", seq_number + 1)

    server_seq_number = generate_sequence_number()
    # Send FIN segment with sequence number + 1
    fin_packet = struct.pack("!B", server_seq_number) + b"FIN"
    server_socket.sendto(fin_packet, client_address)
    print("Server: FIN sent to client with sequence number:", server_seq_number)

    # Wait for ACK from client for server's FIN
    while True:
        try:
            server_socket.settimeout(TIMEOUT)
            acknowledgment, _ = server_socket.recvfrom(1024)
            ack_seq_number = struct.unpack("!B", acknowledgment[:1])[0]
            if acknowledgment[1:] == b"ACK" and ack_seq_number == server_seq_number + 1:
                print("Server: FIN ACK received from client for server's FIN with sequence number:", ack_seq_number)
                break
            if acknowledgment[1:] == b"FIN":
                server_socket.sendto(ack_packet, client_address)
                print("Server: ACK sent to client with acknowledgment number:", seq_number + 1)
        except socket.timeout:
            print("Server: Timeout occurred while waiting for ACK from client. Retrying...")
            # Resend FIN packet
            server_socket.sendto(fin_packet, client_address)
            print("Server: FIN resent to client with sequence number:", server_seq_number)

    # Close socket
    server_socket.close()


def get_request(student_id):
    http_request = f"GET /student/{student_id} HTTP/1.0\r\n\r\n"
    return http_request.encode()


def post_request(student_name):
    http_request = f"POST /student HTTP/1.0\r\nContent-Length: {len(student_name)}\r\n\r\n{student_name}"
    return http_request.encode()



