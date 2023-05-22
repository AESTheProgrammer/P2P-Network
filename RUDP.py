import socket
import crcmod.predefined
import sys
import zlib
import base64
from PIL import Image
import io
import binascii


PACKET_SIZE = 1024
CHECKSUM_SIZE = 4
SEQ_NUM_SIZE = 4

# Set up the receiver
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_address = ("127.0.0.1", 5555)
sock.bind(receiver_address)
chunk_size = PACKET_SIZE - CHECKSUM_SIZE - SEQ_NUM_SIZE
crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')

print("Do Ctrl+c to exit the program !!")

def verify_checksum(packet: bytes):
    packet_size = len(packet)
    received_checksum = int.from_bytes(packet[packet_size - CHECKSUM_SIZE:], 'big')
    data = packet[:packet_size - CHECKSUM_SIZE - SEQ_NUM_SIZE]
    calculated_checksum = calculate_checksum(data)
    return received_checksum == calculated_checksum


def calculate_checksum(data):
    return zlib.crc32(data)


def pack_img(image_path: str = './image.png') -> []:
    # Load the  
    with open(image_path, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    image_bytes = bytes(my_string)
    image_size = len(image_bytes)
    print(image_size)
    total_packets = (image_size + SEQ_NUM_SIZE) // chunk_size + 1
    print(total_packets)
    packets = int.to_bytes(total_packets, SEQ_NUM_SIZE, 'big') + image_bytes 
    return (packets, image_size + 4, total_packets)


def save_file_as_img(image_bytes: bytes, img_format: str = "JPEG"):
    image_bytes = base64.b64decode(image_bytes)
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    image.save("new." + img_format.lower(), img_format)
    image.show()


# Let's send data through UDP protocol
def receive_data():
    received_file = bytes()
    seq_num = 0
    expected_seq_num = 0
    packet_left = 1
    while packet_left > 0:
        packet, sender_addr = sock.recvfrom(PACKET_SIZE)
        if verify_checksum(packet):
            packet_seq_num = int.from_bytes(packet[
                                    len(packet) - CHECKSUM_SIZE - SEQ_NUM_SIZE: \
                                    len(packet) - CHECKSUM_SIZE], 'big')
            data = packet[:len(packet) - CHECKSUM_SIZE - SEQ_NUM_SIZE]
            print(packet_seq_num)
            if packet_seq_num == expected_seq_num:
                ack = str(expected_seq_num) + ":ACK"
                sock.sendto(ack.encode(), sender_addr)
                packet_left -= 1
                if expected_seq_num == 0:
                    packet_left = int.from_bytes(data[0:4], 'big') - 1
                    print(packet_left)
                    data = data[4:]
                print(f"packet left: {packet_left}")
                received_file += data
                expected_seq_num += 1
                print(f"received {len(data)} bytes")
        else:
            print("packet corrupted")
    print(len(received_file))
    save_file_as_img(received_file, "PNG")
    sock.close()


# send data through UDP protocol
def send_data():
    global chunk_size
    seq_num = 0
    packets, file_size, total_packets = pack_img()
    receiver_addr = ('127.0.0.1', 5555)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # 3. setting a 2sec timer for timeout
    for i in range(0, file_size, chunk_size):
        while True:
            send_data = packets[i: i + chunk_size]
            # 1. adding sequence number for an in-order receive
            # 2. calculating checksum of the packet and adding it to packet
            checksum = (calculate_checksum(send_data)).to_bytes(CHECKSUM_SIZE, 'big')
            send_data += int.to_bytes(seq_num, SEQ_NUM_SIZE, 'big') + checksum 
            sock.sendto(send_data, receiver_addr)
            try:
                ack, address = sock.recvfrom(PACKET_SIZE)
                ack = ack.decode()
                ack_seq_num = int(ack.split(':')[0])
                if ack_seq_num == seq_num:  # if the sequence number doesn't match it is a nack
                    seq_num += 1
                    break
            except socket.timeout:
                continue
    sock.close()


def main():


if __name__ == '__main__':
    main()
