import threading
import keyboard
import config
import socket
from API import *
import utils
import sys
import pyaudio
import time
import pickle

print("VoiceSockets testing")
lock = threading.Lock()
key = utils.load_key(config.key_path)
muted = False

def mute():
    global muted
    muted = not muted
    print(f"\n{"Muted" if muted else "Unmuted"}")

keyboard.add_hotkey("shift+v", mute)

sock = socket.socket()
audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=22050,
    input=True,
    frames_per_buffer=1024,
)
sock.connect((config.ip, config.port))
users = {}
utils.send(sock, utils.encrypt(Auth(config.password).serialize(), key))
print("Connected to server.")
def receiver():
    global buffer
    global uerrors
    uerrors = 0
    buffer = b""
    while True:
        data = sock.recv(1024 * 1024)
        if not data:
            break
        buffer += data
        for some_data in buffer.split(b"OILOPAKETSTART!")[1:]:
            try:
                paket = pickle.loads(utils.decrypt(some_data, key))
                handle_object(paket)
                buffer = buffer.replace(b"OILOPAKETSTART!" + some_data, b"")
            except pickle.UnpicklingError:
                uerrors += 1

def SVOdka():
    while True:
        print(f"\rStatus: UnpicklingErrors count:{uerrors}, buffer size:{sys.getsizeof(buffer)}, users in channel:{len(users)+1}",end="")
        time.sleep(1)


def handle_object(netobject):
    if isinstance(netobject, Message):
        _stream = users.get(netobject.send_from)
        if _stream:
            _stream.write(netobject.data)
        return

    if isinstance(netobject, UserConnected):
        if netobject.id in users:
            return

        print(f"\n{netobject.id} connected")

        users[netobject.id] = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=22050,
            output=True,
            frames_per_buffer=1024,
        )
        return

    if isinstance(netobject, UserDisconnected):
        print(f"\n{netobject.id} disconnected")
        if netobject.id in users:
            del users[netobject.id]
            return

    if isinstance(netobject, Channels):
        for i, channel in enumerate(netobject.channels):
            print(f"{i} - {channel} [{netobject.channels[channel]} users]")
        while True:
            try:
                index = utils.get_int("Enter index: ")
                channel = list(netobject.channels.keys())[index]
                break
            except:
                pass
        utils.send(sock, utils.encrypt(pickle.dumps(Channel(channel)), key))
        print(f"Connected to {channel}. Now you can talk with other idiots.")
        threading.Thread(target=SVOdka).start()
        threading.Thread(target=sender).start()
        return


def sender():
    global muted

    while True:
        if muted:
            time.sleep(0.1)
            continue
        data = stream.read(1024)
        netobject = Message(data)
        encrypted_data = utils.encrypt(pickle.dumps(netobject), key)
        utils.send(sock, encrypted_data)

threading.Thread(target=receiver).start()