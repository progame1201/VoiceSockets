import time

import config
import socket
import pickle
import uuid
import threading
from API import *
import utils

channels = {"channel1": [], "channel2": []}  # channel:client


class Client:
    def __init__(self, sock, address):
        self.sock: socket.socket = sock
        self.address = address
        self.id = str(uuid.uuid4())
        self.authorized = False

        self.cant_send = False
        self.cant_hear = False

        self.key = utils.load_key(config.key_path)
        self.channel = None
        #users[self.id] = self.sock

        self.receiver()

    def disconnect(self):
        self.broadcast_to_channel(UserDisconnected(self.id))
        self.sock.close()
        if self.channel:
            if self.id in [client.id for client in channels[self.channel]]:
                del channels[self.channel][self]
        print(f"User {self.id} disconnected")

    def broadcast_to_channel(self, netobject):
        if not self.channel:
            return
        if self.cant_send:
            return
        for client in channels[self.channel]:
            if client.sock == self.sock:
                continue

            if client.cant_hear:
                continue

            try:
                utils.send(client.sock, utils.encrypt(netobject.serialize(), self.key))
            except:
                pass

    def receiver(self):
        try:
            errors = 0
            buffer = b""
            while True:
                data = self.sock.recv(1024 * 1024)
                if not data:
                    break
                buffer += data

                for some_data in buffer.split(b"OILOPAKETSTART!")[1:]:
                    if errors >= config.errors_limit:
                        print("Errors limit exceeded")
                        self.disconnect()
                        break
                    try:
                        paket = pickle.loads(utils.decrypt(some_data, self.key))
                        self.handle_object(paket)
                        buffer = buffer.replace(b"OILOPAKETSTART!" + some_data, b"")
                    except pickle.UnpicklingError:
                        errors += 1
                        print("UnpicklingError")
                errors = 0
        except:
            print("R:D")
            self.disconnect()

    def handle_object(self, obj: NetObject):
        try:
            if isinstance(obj, Message):
                if not self.authorized or not self.channel:
                    print("M:D")
                    self.disconnect()
                obj.send_from = self.id
                self.broadcast_to_channel(obj)
            if isinstance(obj, Auth):
                if config.password == obj.password:
                    self.authorized = True
                    self.id = f"{self.id}--{obj.nickname}"
                    print(f"{self.id} Authorized")
                    _channels = {}
                    for channel in channels:
                        _channels[channel] = len(channels[channel])
                    utils.send(self.sock, utils.encrypt(Channels(_channels).serialize(), self.key))
                else:
                    print("A:D")
                    self.disconnect()

            if isinstance(obj, Channel):
                if not self.authorized:
                    self.disconnect()
                    print("A1:D")
                if obj.channel in channels:
                    self.channel = obj.channel

                    for client in channels[self.channel]:
                        utils.send(self.sock, utils.encrypt(UserConnected(client.id).serialize(), self.key))

                    channels[obj.channel].append(self)
                    self.broadcast_to_channel(UserConnected(self.id))
                    print(f"User {self.id} joined channel {obj.channel}")
        except:
            self.disconnect()
