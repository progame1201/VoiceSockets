import threading
import keyboard
import config
import socket
from API import *
import utils
from colorama import init, Fore
import sys
import pyaudio
import time
import os
import pickle
init(autoreset=True)


print(f"VoiceSockets 1.0.2, progame1201")
print(f"You will be connected to {config.ip}:{config.port}")
print(f"Mute hotkey: {config.mute_hotkey}")

if os.path.exists("nickname") and config.auto_load_last_nickname:
    with open("nickname", "r") as file:
        nickname = file.read().strip()
    print(f"Auto loaded nickname: {nickname}")
else:
    nickname = input("Enter your nickname:").strip()
    with open("nickname", "w") as file:
        file.write(nickname)
audio = pyaudio.PyAudio()
micro_index = None

if config.choose_micro_on_start:
    print("Choose microphone")
    for i in range(0, 1000):
        try:
            print(f"{i} - {audio.get_device_info_by_index(i)['name']}")
        except:
            break
    micro_index = utils.get_int("Enter index: ")

key = utils.load_key(config.key_path)
muted = False

def mute():
    global muted
    muted = not muted
    #print(f"\n{f"{Fore.RED}Muted" if muted else f"{Fore.GREEN}Unmuted"}")

keyboard.add_hotkey(config.mute_hotkey, mute)

sock = socket.socket()

if micro_index:
    stream = audio.open(
        format=pyaudio.paInt16,
        input_device_index=micro_index,
        channels=1,
        rate=22050,
        input=True,
        frames_per_buffer=1024,
    )
else:
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=22050,
        input=True,
        frames_per_buffer=1024,
    )

sock.connect((config.ip, config.port))
users = {}
muted_users = []
utils.send(sock, utils.encrypt(Auth(config.password, nickname).serialize(), key))
print(f"{Fore.GREEN}Connected to server.")

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
        print(f"\rStatus: UnpicklingErrors count:{uerrors}, buffer size:{sys.getsizeof(buffer)}, users in channel:{len(users)+1}, muted: {"yes" if muted else "no"} [{config.mute_hotkey}]",end=f"{" "*10}")
        time.sleep(3)


def handle_object(netobject):
    if isinstance(netobject, Message):
        _stream = users.get(netobject.send_from)
        if _stream:
            _stream.write(netobject.data)
        return

    if isinstance(netobject, UserConnected):
        if netobject.id in users:
            return

        print(f"\r{Fore.GREEN}{netobject.id.split("--")[1]} connected{" "*60}")
        users[netobject.id] = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=22050,
            output=True,
            frames_per_buffer=1024,
        )
        return

    if isinstance(netobject, UserDisconnected):
        print(f"\r{Fore.RED}{netobject.id.split("--")[1]} disconnected{" "*60}")
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
        print(f"Connected to {channel}. Now you can talk with other nerds.")
        threading.Thread(target=commands).start()
        threading.Thread(target=SVOdka, daemon=True).start()
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

def commands():

    while True:
        try:
            command = input("").lower()
            if command.startswith("mute"):
                args = command.split(" ")[1:]
                if args[0] == "list":
                    for id in users:
                        print(id)
                    continue
                if args[0] in list(users.keys()):
                    muted_users.append(args[0])
                    users.pop(args[0])
            if command.startswith("unmute"):
                args = command.split(" ")[1:]
                if args[0] == "list":
                    for id in muted_users:
                        print(id)
                    continue
                if args[0] in muted_users:
                    muted_users.remove(args[0])
                    users[args[0]] = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=22050,
                    output=True,
                    frames_per_buffer=1024,
                    )
        except Exception as ex:
            print(f"Error: {ex}")
threading.Thread(target=receiver).start()