import socket
import struct
import time
import random

from TCPOverUDP import client_handshake

# Constants for network parameters and window size
SERVER_IP = "localhost"
SERVER_PORT = 12345
WINDOW_SIZE = 5  # Initial window size
TIMEOUT = 1  # Timeout for receiving ACK in seconds

# Define global variables for tracking window state
base_seq_number = 0
next_seq_number = 0
max_seq_number = 100
window = []

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_packet(packet, seq_number):
    global client_socket
    global window
    global base_seq_number
    global next_seq_number

    # Send packet to server
    packet_with_seq_num = struct.pack("!B", seq_number) + packet
    client_socket.sendto(packet_with_seq_num, (SERVER_IP, SERVER_PORT))
    window.append(seq_number)
    next_seq_number += 1


def receive_ack():
    global client_socket
    global window
    global base_seq_number

    client_socket.settimeout(TIMEOUT)
    try:
        ack_packet_with_seq_num, _ = client_socket.recvfrom(1024)
        ack_seq_number = struct.unpack("!B", ack_packet_with_seq_num[:1])[0]
        if ack_seq_number in window:
            window.remove(ack_seq_number)
            base_seq_number = ack_seq_number + 1
    except socket.timeout:
        print("Timeout occurred while waiting for ACK.")
        pass


def main():
    global base_seq_number
    global next_seq_number

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
        b"POST Yasmine hani",
        b"GET 100"
        # Add more data packets as needed
    ]

    while base_seq_number < max_seq_number:
        # Send packets within the window size
        while next_seq_number < base_seq_number + WINDOW_SIZE and next_seq_number < max_seq_number:
            send_packet(data_packets[next_seq_number], next_seq_number)

        # Receive acknowledgments and slide window
        receive_ack()

    # Close socket
    client_socket.close()

if __name__ == "__main__":
    main()
