import requests
from requests.exceptions import HTTPError
import json

# Set the server address and port
SERVER_ADDRESS = 'http://localhost'
SERVER_PORT = 8000

my_user_id = ""
my_ip = ""


def get_user_ip(user_id: str) -> str:
    """ get ip address mapped to a user-id """
    DIRECTORY = f'/users/{user_id}'
    response = requests.get(f"{SERVER_ADDRESS}:{SERVER_PORT}{DIRECTORY}")
    if response.status_code == 200:
        peer_ip = response.text
        print(f'IPv4 address: {peer_ip}')
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


def register(user_id: str, ip: str) -> str:
    """ register with the STUN server """
    DIRECTORY = f'/users'
    info = {
            'user-id': user_id,
            'ip': ip
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
    while True:
        print("request: ")
        req = input()
        if req == "1":
            print('user id: ', end='')
            my_user_id = input()
            print('\nip: ', end='')
            my_ip = input()
            print()
            register(my_user_id, my_ip)
        elif req == "2":
            print('user id: ', end='')
            user_id = input()
            get_user_ip(user_id)
        elif req == "3":
            get_users_id()
        elif req == "4":
            break
    

if __name__ == "__main__":
    main()
