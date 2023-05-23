import requests
import json
import sys
import subprocess

from time import sleep
from requests.exceptions import HTTPError
from image_util import send_image, receive_image
from doc_util import send_doc, receive_doc

# Set the server address and port
SERVER_ADDRESS = 'http://localhost'
SERVER_PORT = 8000
peer_ip = ""
my_ip = '127.0.0.1'
my_port = int(sys.argv[1])
peer_port = -1


def get_user_ip(user_id: str) -> str:
    """ get ip address mapped to a user-id """
    global peer_ip, peer_port
    DIRECTORY = f'/users/{user_id}'
    response = requests.get(f"{SERVER_ADDRESS}:{SERVER_PORT}{DIRECTORY}")
    if response.status_code == 200:
        peer_ip, peer_port = tuple(response.text.split(":"))
        peer_port = int(peer_port)
        print(f'Address: {response.text}')
    elif response.status_code == 404:
        print(response.reason)
        print(response)
        print("Requested user-id does not exist")


def get_users_id() -> str:
    """ get all user-ids """
    DIRECTORY = f'/users'
    response = requests.get(f"{SERVER_ADDRESS}:{SERVER_PORT}{DIRECTORY}")
    if response.status_code == 200:
        json_data = response.json()
        print('index    user-id')
        for user_id in json_data.keys():
            print(f'{json_data.get(user_id)}. {user_id}')
    else:
        print(response.reason)
        print(response)


def getIP():
    """ return the ip address of the host """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    ip = s.getsockname()[0]
    s.close()
    return ip


def register(user_id: str, ip: str, port: str) -> str:
    """ register with the STUN server """
    DIRECTORY = f'/users'
    info = {
            'user-id': user_id,
            'address': ip + ":" + port
    }
    info = json.dumps(info)
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{SERVER_ADDRESS}:{SERVER_PORT}{DIRECTORY}",\
                            data=info, headers=headers)
    response.raise_for_status()
    if response.status_code == 200:
        print('Success')
    else:
        print(response.reason)
    print(response)


def main():
    if argv[2] != "local":
        my_ip = getIP()
    child_proc = []
    child_proc.append(
        subprocess.Popen(["python3", "image_util.py",
                        f"{int(sys.argv[1])+1}", my_ip]))
    child_proc.append(
        subprocess.Popen(["python3", "doc_util.py",
                        f"{int(sys.argv[1])+3}", my_ip)
    sleep(1)
    while True:
        print("request: ")
        req = input()
        if req == "register":
            print('user id: ')
            my_user_id = input()
            #print('ip: ')
            #my_ip = input()
            print()
            register(my_user_id, my_ip, str(my_port))
        elif req == "resolve":
            print('user id: ', end='')
            user_id = input()
            get_user_ip(user_id)
        elif req == "list":
            get_users_id()
        elif req == "get image":
            print("IMAGE NAME: ")
            down_file = input()
            print("DESTINATION PATH: ")
            dest_path = input()
            receive_image(down_file, dest_path, (peer_ip, peer_port + 1)) 
        elif req == "get doc":
            print("DOC. NAME: ")
            down_file = input()
            print("DESTINATION FILE NAME: ")
            dest_path = input()
            receive_doc(down_file, dest_path, (peer_ip, peer_port + 3)) 
        elif req == "exit":
            break
        else:
            print("Invalid Request.")
    for proc in child_proc:
        proc.kill()

if __name__ == '__main__':
    main()
