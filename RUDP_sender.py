import socket
import sys
import crcmod.predefined
import zlib
import io
from PIL import Image
import base64

# Set the packet size for each chunk
PACKET_SIZE = 1024
CHECKSUM_SIZE = 4
SEQ_NUM_SIZE = 4
chunk_size = PACKET_SIZE - CHECKSUM_SIZE - SEQ_NUM_SIZE

# 3. setting a 2sec timer for timeout
sock.settimeout(2)  

crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-32')

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


def calculate_checksum(data):
    return zlib.crc32(data)


# send data through UDP protocol
def send_data():
    global chunk_size
    seq_num = 0
    packets, file_size, total_packets = pack_img()
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
    # Set up the sender
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_addr = ('127.0.0.1', 5555)
    send_data()


if __name__ == "__main__":
    main()
