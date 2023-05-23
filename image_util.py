import socket
import crcmod.predefined
import sys
import zlib
import base64
from PIL import Image
import io
import binascii
import os
import select
import random


PACKET_SIZE = 1024
CHECKSUM_SIZE = 4
SEQ_NUM_SIZE = 4
SEND_PORT = int(sys.argv[1])
RECV_PORT = int(sys.argv[1]) + 1
MY_IP = "127.0.0.1"

# Set up the receiver
chunk_size = PACKET_SIZE - CHECKSUM_SIZE - SEQ_NUM_SIZE
crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')


def verify_checksum(packet: bytes):
    packet_size = len(packet)
    received_checksum = int.from_bytes(packet[packet_size - CHECKSUM_SIZE:], 'big')
    data = packet[:packet_size - CHECKSUM_SIZE - SEQ_NUM_SIZE]
    calculated_checksum = calculate_checksum(data)
    return received_checksum == calculated_checksum


calculate_checksum = lambda data: zlib.crc32(data)
check_file_existence = lambda file_name:\
                        os.path.exists(os.path.join(".", file_name))
extract_file_extension = lambda file_name:\
                            (os.path.splitext(file_name))[1][1:]


def pack_img(image_path: str) -> []:
    with open(image_path, "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    image_bytes = bytes(my_string)
    image_size = len(image_bytes)
    print(image_size)
    total_packets = (image_size + SEQ_NUM_SIZE) // chunk_size + 1
    print(total_packets)
    packets = int.to_bytes(total_packets, SEQ_NUM_SIZE, 'big') + image_bytes 
    return (packets, image_size + 4, total_packets)


def save_file_as_img(image_bytes:bytes, img_format, dest):
    image_bytes = base64.b64decode(image_bytes)
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    image.save(dest, img_format)
    image.show()


def receive_image(src_file:str, dest_path:str, peer_addr:()):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    received_file = bytes()
    seq_num, packet_left, expected_seq_num = 0, 1, 0
    sock.sendto(src_file.encode(), peer_addr)
    while packet_left > 0:
        packet, sender_addr = sock.recvfrom(PACKET_SIZE)
        if verify_checksum(packet):
            packet_seq_num = int.from_bytes(packet[
                                    len(packet) - CHECKSUM_SIZE - SEQ_NUM_SIZE: \
                                    len(packet) - CHECKSUM_SIZE], 'big')
            data = packet[:len(packet)-CHECKSUM_SIZE-SEQ_NUM_SIZE]
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
    print("received file size: " + str(len(received_file)))
    save_file_as_img(received_file, extract_file_extension(dest_path), dest_path)
    sock.close()


def send_image():
    global chunk_size
    print(f'{sys.argv[0]} running')
    seq_num = 0
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    send_sock.bind((MY_IP, SEND_PORT))
    while True:
        ready = select.select([send_sock], [], [])
        if not ready[0]:
            continue
        packet, receiver_addr = send_sock.recvfrom(PACKET_SIZE)
        img_path = packet.decode().strip()
        packets, file_size, total_packets = pack_img(img_path)
        if not check_file_existence(img_path):
            send_sock.sendto("File not available!\n".encode(), receiver_addr)
            continue
        send_sock.settimeout(4)  # 1. setting a 4sec timer for timeout
        for i in range(0, file_size, chunk_size):
            while True:
                send_data = packets[i: i + chunk_size]
                # 2. adding sequence number for an in-order receive
                # 3. calculating checksum of the packet and adding it to packet
                checksum = (calculate_checksum(send_data)).to_bytes(CHECKSUM_SIZE, 'big')
                send_data += int.to_bytes(seq_num, SEQ_NUM_SIZE, 'big') + checksum 
                send_sock.sendto(send_data, receiver_addr)
                try:
                    address = ""
                    while address != receiver_addr: 
                        ack, address = send_sock.recvfrom(PACKET_SIZE)
                    ack = ack.decode()
                    ack_seq_num = int(ack.split(':')[0])
                    if ack_seq_num == seq_num:  # if the sequence number doesn't match it is a nack
                        seq_num += 1
                        break
                except socket.timeout:
                    continue
    send_sock.close()


if __name__ == '__main__':
    MY_IP = sys.argv[2]
    send_image()

