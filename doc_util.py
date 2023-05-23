import socket
import threading
import os
import sys

MAX_FILE_NAME_LEN = 128
SEND_PORT = int(sys.argv[1])
MY_IP = sys.argv[2]


check_file_existence = lambda file_name: \
                    os.path.exists(os.path.join('.', file_name))


def receive_doc(requested_file: str, dest_path: str, peer_addr): 
    if not check_file_existence(requested_file):
        client_socket.sendall("File not available.\n".encode())
        return
    print("file ", end='')
    print(requested_file)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(peer_addr)
    print('Connected to server.')
    client_socket.sendall(requested_file.encode())
    file_size = int(client_socket.recv(8).decode())
    file_data = client_socket.recv(file_size)
    with open(dest_path, 'wb') as file:
        file.write(file_data)
        print('File received and saved.')
        client_socket.close()


def send_doc():
    print(f'{sys.argv[0]} running')
    FILE_PATH = 'file.txt'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'{MY_IP}:{SEND_PORT}')
    server_socket.bind((MY_IP, SEND_PORT))
    server_socket.listen(3)
    while True:
        print('Waiting for TCP connection...')
        client_socket, address = server_socket.accept()
        print('Connected to:', address)
        requested_file = (client_socket.recv(MAX_FILE_NAME_LEN).decode()).strip()
        print('Requested file:', requested_file)
        if not check_file_existence(requested_file):
            print("debug")
            client_socket.sendall("File not available!\n".encode())
            client_socket.close()
            print("debug")
            continue
        print('Requested file:', requested_file)
        with open(requested_file, 'rb') as a_file:
            file_data = a_file.read()
            file_size = len(file_data)
            print(f"file size: {file_size}")
            client_socket.sendall(str(file_size).rjust(8).encode())
            client_socket.sendall(file_data)
        client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    send_doc()
