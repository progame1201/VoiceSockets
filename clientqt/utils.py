from Crypto.Cipher import AES
import pickle
import socket
from Crypto.Util import Counter


def _decrypt(connected_information, key):
    """Расшифровывает данные с помощью AES (режим CBC)"""
    cipher = AES.new(key, AES.MODE_CTR, counter=connected_information[1])
    decrypted_data = cipher.decrypt(connected_information[0])
    return decrypted_data


def _encrypt(data, key):
    """Шифрует данные с помощью AES (режим CBC)"""
    ctr = Counter.new(128)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    encrypted_data = cipher.encrypt(data)
    return [encrypted_data, ctr]


def decrypt(data, key):
    return _decrypt(pickle.loads(data), key)


def encrypt(data, key):
    return pickle.dumps(_encrypt(data, key))

def load_key(path):
    with open(path, 'rb') as f:
        return f.read()

def get_int(string):
    while True:
        try:
            return int(input(string))
        except:
            print("Enter a number!")

def send(sock, data):
    sock.send(b"OILOPAKETSTART!"+data)