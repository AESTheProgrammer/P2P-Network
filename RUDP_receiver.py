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


def main():
    data = receive_data()
    sock.close()


if __name__ == '__main__':
    main()
