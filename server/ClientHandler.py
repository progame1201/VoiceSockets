import time

import config
import socket
import pickle
import uuid
import threading
from API import *
import utils
channels = {"channel 1":{}, "channel 2":{}} # channel:id:sock

class ClientHandler:
    def __init__(self, sock, address):
        self.sock:socket.socket = sock
        self.address = address
        self.id = str(uuid.uuid4())
        self.authorized = False
        self.key = utils.load_key(config.key_path)
        self.channel = None
        #users[self.id] = self.sock

        self.receiver()

    def disconnect(self):
        self.broadcast_to_channel(UserDisconnected(self.id))
        self.sock.close()
        if self.channel:
            if self.id in channels[self.channel]:
                del channels[self.channel][self.id]
        print(f"User {self.id} disconnected")

    def broadcast_to_channel(self, netobject):
        if not self.channel:
            return
        for conn in channels[self.channel].values():
            if conn != self.sock:
                try:
                    utils.send(conn, utils.encrypt(netobject.serialize(), self.key))
                except:
                    pass

    def receiver(self):
        try:
            buffer = b""
            while True:
                data = self.sock.recv(1024 * 1024)
                if not data:
                    break
                buffer += data

                for some_data in buffer.split(b"OILOPAKETSTART!")[1:]:
                    try:
                        paket = pickle.loads(utils.decrypt(some_data, self.key))
                        self.handle_object(paket)
                        buffer = buffer.replace(b"OILOPAKETSTART!"+some_data, b"")
                    except pickle.UnpicklingError:
                        print("UnpicklingError")
        except:
            print("R:D")
            self.disconnect()


    def handle_object(self, obj:NetObject):
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
                    print(f"{self.id} Authorized")
                    _channels = {}
                    for channel in channels.keys():
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

                    for id in channels[self.channel]:
                        utils.send(self.sock, utils.encrypt(UserConnected(id).serialize(), self.key))

                    channels[obj.channel][self.id] = self.sock
                    self.broadcast_to_channel(UserConnected(self.id))
                    print(f"User {self.id} joined channel {obj.channel}")
        except:
            self.disconnect()