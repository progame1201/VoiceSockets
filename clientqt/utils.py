from Crypto.Cipher import AES
import json
import base64
from Crypto.Util import Counter
import binascii

def encode_bytes(obj):
    # thx gpt
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, dict):
        return {key: encode_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [encode_bytes(item) for item in obj]
    else:
        return obj

def decode_bytes(obj):
    # thx gpt
    if isinstance(obj, str):
        try:
            return base64.b64decode(obj)
        except (ValueError, binascii.Error):
            return obj
    elif isinstance(obj, dict):
        return {key: decode_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [decode_bytes(item) for item in obj]
    else:
        return obj

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
    loaded_data = json.loads(data.decode())
    encrypted_data = decode_bytes(loaded_data[0])
    iv = decode_bytes(loaded_data[1])
    return _decrypt([encrypted_data, iv], key)


def encrypt(data, key):
    encrypted_data = _encrypt(data, key)
    return json.dumps([encode_bytes(encrypted_data[0]), encode_bytes(encrypted_data[1])]).encode()

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