import socket
import struct

# Constants for network parameters and window size
CLIENT_IP = "localhost"
CLIENT_PORT = 12345

# Define global variables for tracking window state
expected_seq_number = 0
recv_window_size = 5  # Receive window size
recv_window = []

# Create UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((CLIENT_IP, CLIENT_PORT))


def receive_packet():
    global server_socket
    global expected_seq_number
    global recv_window
    global recv_window_size

    packet_with_seq_num, client_address = server_socket.recvfrom(1024)
    seq_number = struct.unpack("!B", packet_with_seq_num[:1])[0]
    packet = packet_with_seq_num[1:]

    if seq_number == expected_seq_number:
        # Packet received in order, deliver to application layer
        print("Packet received:", packet.decode())
        expected_seq_number += 1

        # Slide window and deliver in-order packets
        while expected_seq_number in recv_window:
            recv_window.remove(expected_seq_number)
            expected_seq_number += 1
    elif seq_number < expected_seq_number + recv_window_size:
        # Packet out of order, buffer in receive window
        recv_window.append(seq_number)
        send_ack(expected_seq_number - 1, client_address)  # Acknowledge last in-order packet
    else:
        # Packet outside of receive window, discard or ignore
        pass


def send_ack(ack_seq_number, client_address):
    global server_socket
    ack_packet = struct.pack("!B", ack_seq_number) + b"ACK"
    server_socket.sendto(ack_packet, client_address)


def main():
    while True:
        receive_packet()

if __name__ == "__main__":
    main()
