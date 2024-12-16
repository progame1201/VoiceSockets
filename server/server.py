import config
import socket
import ClientHandler
import threading

sock = socket.socket()
sock.bind((config.ip, config.port))
sock.listen(15)

while True:
    socket, addr = sock.accept()
    print(f"{addr} Connected")
    threading.Thread(target=lambda:ClientHandler.ClientHandler(socket, addr)).start()