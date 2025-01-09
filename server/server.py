import config
import socket
from utils import log
import Client
import threading

sock = socket.socket()
sock.bind((config.ip, config.port))
sock.listen(15)
log("Server bound.")
log("Commands:")
log("mute - mute some person. mute <mode 1 - cant_hear, 2 - cant_send> <channel_name> <client_id>\nkick - kick some person. kick <client_id>")
def commands():

    while True:
        try:
            command = input("")
            if command.startswith("mute"):
                args = command.split(" ")[1:]
                if args[0] == "1":
                    for client in Client.channels[args[1]]:
                        if client.id in args[2]:
                            client.cant_hear = not client.cant_hear
                            log(f"cant_hear {"muted" if client.cant_hear else "unmuted"}")
                if args[0] == "2":
                    for client in Client.channels[int(args[1])]:
                        if client.id in args[2]:
                            client.cant_send = not client.cant_send
                            log(f"cant_send {"muted" if client.cant_send else "unmuted"}")
            if command.startswith("kick"):
                args = command.split(" ")[1:]
                for channel in Client.channels:
                    for client in Client.channels[channel]:
                        if client.id == args[0]:
                            client.disconnect()
                            break
        except Exception as ex:
            log(f"Error: {ex}")

threading.Thread(target=commands).start()
while True:
    socket, addr = sock.accept()
    log(f"{addr} Connected")
    threading.Thread(target=lambda:Client.Client(socket, addr)).start()



