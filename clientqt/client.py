import threading
import keyboard
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QMimeData
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QComboBox, QWidget, QListWidget, QLabel
from PyQt6 import uic
import time
import utils
import pyaudio
import config
import socket
import os
import sys
from API import *
import pickle

muted = False
audio = pyaudio.PyAudio()
key = utils.load_key(config.key_path)
users = {}
muted_users = []


def sender(micro):
    global muted
    if micro:
        stream = audio.open(
            format=pyaudio.paInt16,
            input_device_index=int(micro),
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
    while True:
        if muted:
            time.sleep(0.1)
            continue
        data = stream.read(1024)
        netobject = Message(data)
        encrypted_data = utils.encrypt(pickle.dumps(netobject), key)
        utils.send(sock, encrypted_data)

class receiver(QObject):
    user_connected = pyqtSignal(str)
    user_disconnected = pyqtSignal(str)
    set_channel = pyqtSignal(dict)
    mute_btn_upd = pyqtSignal()
    update_status = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.channel = None
        self.micro = None

    def receiver(self):
        global buffer
        global uerrors
        uerrors = 0
        buffer = b""
        threading.Thread(target=self.status_updater).start()
        keyboard.add_hotkey(config.mute_hotkey, self.hotkey_mute)
        while True:
            data = sock.recv(1024 * 1024)
            if not data:
                break
            buffer += data
            for some_data in buffer.split(b"OILOPAKETSTART!")[1:]:
                try:
                    paket = pickle.loads(utils.decrypt(some_data, key))
                    self.handle_object(paket)
                    buffer = buffer.replace(b"OILOPAKETSTART!" + some_data, b"")
                except pickle.UnpicklingError:
                    uerrors += 1
    def hotkey_mute(self):
        global muted
        muted = not muted
        self.mute_btn_upd.emit()

    def status_updater(self):
        while True:
            self.update_status.emit()
            time.sleep(2)

    def handle_object(self, netobject):
        if isinstance(netobject, Message):
            _stream = users.get(netobject.send_from)
            if _stream:
                _stream.write(netobject.data)
            return

        if isinstance(netobject, UserConnected):
            if netobject.id in users:
                return

            print(f"{netobject.id.split("--")[1]} connected{" " * 60}")
            users[netobject.id] = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=22050,
                output=True,
                frames_per_buffer=1024,
            )
            self.user_connected.emit(netobject.id)
            return

        if isinstance(netobject, UserDisconnected):
            print(f"{netobject.id.split("--")[1]} disconnected{" " * 60}")
            if netobject.id in users:
                self.user_disconnected.emit(netobject.id)
                del users[netobject.id]
                return

        if isinstance(netobject, Channels):
            self.set_channel.emit(netobject.channels)
            while self.channel is None:
                time.sleep(0.1)
            utils.send(sock, utils.encrypt(pickle.dumps(Channel(self.channel)), key))
            print(f"Connected to {self.channel}. Now you can talk with other nerds.")
            threading.Thread(target=lambda:sender(self.micro)).start()
            return


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'ui.ui', self)
        self.channel_selct: QWidget
        self.start_settings_select:QWidget
        self.users: QListWidget
        self.channel_list: QComboBox
        self.mute_button: QPushButton
        self.mute_selected:QPushButton
        self.micro: QComboBox
        self.nickname_input: QLineEdit
        self.save: QPushButton
        self.statuslabel:QLabel
        self.on_voice_chat:QWidget


        self.on_voice_chat.hide()
        self.channel_selct.hide()
        self.channel_list.addItem("Choose")

        if os.path.exists("nickname") and config.auto_load_last_nickname:
            with open("nickname", "r") as file:
                nickname = file.read().strip()
            self.nickname_input.setText(nickname)
            print(f"Auto loaded nickname: {nickname}")


        mircos = {}
        for i in range(0, 1000):
            try:
                mircos[i] = audio.get_device_info_by_index(i)['name']
            except:
                break
        self.micro.addItem("Default", "default")
        for index in mircos:
            self.micro.addItem(mircos[index], index)

        self.thread = QThread()
        self.worker = receiver()
        self.worker.moveToThread(self.thread)

        self.worker.set_channel.connect(self.show_channels)
        self.worker.user_disconnected.connect(self.user_disconnected)
        self.worker.user_connected.connect(self.user_connected)
        self.worker.mute_btn_upd.connect(self.upd_mute_button)
        self.worker.update_status.connect(self.status_label_upd)

        self.thread.start()
        self.thread.started.connect(self.worker.receiver)

        self.mute_button.clicked.connect(self.mute)
        self.micro.currentTextChanged.connect(self.select_micro)
        self.save.clicked.connect(self.auth)
        self.mute_selected.clicked.connect(self.mute_selected_user)
        self.users.itemClicked.connect(self.on_item_clicked)
        self.channel_list.currentTextChanged.connect(self.select_channel)

    def auth(self):
        with open("nickname", "w") as file:
            file.write(self.nickname_input.text())
        self.start_settings_select.hide()
        utils.send(sock, utils.encrypt(Auth(config.password, self.nickname_input.text()).serialize(), key))

    def mute(self):
        global muted
        muted = not muted
        self.mute_button.setText("Unmute" if muted else "Mute")

    def on_item_clicked(self, item):
        self.mute_selected.setText("unmute selected user" if item.text() in muted_users else "mute selected user")

    def upd_mute_button(self):
        self.mute_button.setText("Unmute" if muted else "Mute")

    def show_channels(self, channels):
        for channel in channels:
            self.channel_list.addItem(channel)
        self.channel_selct.show()

    def mute_selected_user(self):
        items = self.users.selectedItems()
        if not items:
            return
        for item in items:
            if item.text() not in muted_users:
                muted_users.append(item.text())
                users.pop(item.text())
            else:
                muted_users.remove(item.text())
                users[item.text()] = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=22050,
                    output=True,
                    frames_per_buffer=1024,
                )
        self.mute_selected.setText("unmute selected user" if item.text() in muted_users else "mute selected user")

    def status_label_upd(self):
        self.statuslabel.setText(f"Status: decode errors: {uerrors}; buffer size: {sys.getsizeof(buffer)};")

    def select_channel(self):
        if self.channel_list.currentText() == "Choose":
            return
        self.worker.channel = self.channel_list.currentText()
        self.channel_selct.hide()
        self.on_voice_chat.show()

    def user_connected(self, id):
        self.users.addItem(id)

    def select_micro(self, index):
        if index == "default":
            return
        self.worker.micro = index


    def user_disconnected(self, id):
        try:
            for item in [self.users.item(i) for i in range(self.users.count())]:
                if item.text() == id:
                    self.users.takeItem(self.users.row(item))
        except Exception as ex:
            print(ex)

if __name__ == "__main__":
    sock = socket.socket()
    sock.connect((config.ip, config.port))

    app = QApplication(sys.argv)
    ex = App()
    app.setStyle('windows11')
    ex.show()
    sys.exit(app.exec())
