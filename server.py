from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

HOST = "192.168.1.105"
PORT = 3000
BufferSize = 1024
addresses = {}
clients = {}


def Connections():
    while True:
        clientText, addr = server.accept()
        print("{} is connected!!".format(addr))
        addresses[clientText] = addr
        Thread(target=ClientConnection, args=(clientText,)).start()


def ClientConnection(client):
    while True:
        try:
            data = client.recv(BufferSize).decode("utf-8")
            Broadcast(data)
        except:
            continue


def Broadcast(msg):
    for sockets in addresses:
        sockets.send(msg.encode("utf-8"))


server = socket(family=AF_INET, type=SOCK_STREAM)
try:
    server.bind((HOST, PORT))
except OSError:
    print("Server Busy")


server.listen(2)
print("Waiting for Connections... ")
AcceptThread = Thread(target=Connections)
AcceptThread.start()
AcceptThread.join()
server.close()
