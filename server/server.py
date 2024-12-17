import config
import socket
import Client
import threading

sock = socket.socket()
sock.bind((config.ip, config.port))
sock.listen(15)
print("Server bound.")
print("Commands:")
print("mute - mute some person. mute <mode 1 - cant_hear, 2 - cant_send> <channel_name> <client_id>")
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
                            print(f"cant_hear {"muted" if client.cant_hear else "unmuted"}")
                if args[0] == "2":
                    for client in Client.channels[int(args[1])]:
                        if client.id in args[2]:
                            client.cant_send = not client.cant_send
                            print(f"cant_send {"muted" if client.cant_send else "unmuted"}")
        except Exception as ex:
            print(f"Error: {ex}")

threading.Thread(target=commands).start()
while True:
    socket, addr = sock.accept()
    print(f"{addr} Connected")
    threading.Thread(target=lambda:Client.Client(socket, addr)).start()



