# Function to find the Checksum of Sent Message

def find_checksum(sent_message, k):
    # Dividing sent message in packets of k bits.
    c1 = sent_message[0:k]
    c2 = sent_message[k:2 * k]
    c3 = sent_message[2 * k:3 * k]
    c4 = sent_message[3 * k:4 * k]

    # Calculating the binary sum of packets
    sum_bits = bin(int(c1, 2) + int(c2, 2) + int(c3, 2) + int(c4, 2))[2:]

    # Adding the overflow bits
    if len(sum_bits) > k:
        x = len(sum_bits) - k
        sum_bits = bin(int(sum_bits[0:x], 2) + int(sum_bits[x:], 2))[2:]
    if len(sum_bits) < k:
        sum_bits = '0' * (k - len(sum_bits)) + sum_bits

    # Calculating the complement of sum
    checksum = ''
    for i in sum_bits:
        if i == '1':
            checksum += '0'
        else:
            checksum += '1'
    return checksum


# Function to find the Complement of binary addition of
# k bit packets of the Received Message + Checksum
def check_receiver_checksum(received_message, k, checksum):
    # Dividing sent message in packets of k bits.
    c1 = received_message[0:k]
    c2 = received_message[k:2 * k]
    c3 = received_message[2 * k:3 * k]
    c4 = received_message[3 * k:4 * k]

    # Calculating the binary sum of packets + checksum
    receiver_sum = bin(int(c1, 2) + int(c2, 2) + int(checksum, 2) +
                       int(c3, 2) + int(c4, 2) + int(checksum, 2))[2:]

    # Adding the overflow bits
    if len(receiver_sum) > k:
        x = len(receiver_sum) - k
        receiver_sum = bin(int(receiver_sum[0:x], 2) + int(receiver_sum[x:], 2))[2:]

    # Calculating the complement of sum
    receiver_checksum = ''
    for i in receiver_sum:
        if i == '1':
            receiver_checksum += '0'
        else:
            receiver_checksum += '1'

    final_sum = bin(int(checksum, 2) + int(receiver_checksum, 2))[2:]

    # Finding the sum of checksum and received checksum
    final_comp = ''
    for i in final_sum:
        if i == '1':
            final_comp += '0'
        else:
            final_comp += '1'

    # If sum = 0, No error is detected
    if int(final_comp, 2) == 0:
        return True
    # Otherwise, Error is detected
    else:
        return False


SentMessage = "10010101011000111001010011101100"
k = 8
ReceivedMessage = "10010101011000111001010011101100"
Checksum = find_checksum(SentMessage, k)
ReceiverChecksum = check_receiver_checksum(ReceivedMessage, k, Checksum)
print("Result: ", ReceiverChecksum)
