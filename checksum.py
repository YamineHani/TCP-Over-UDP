import struct

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
