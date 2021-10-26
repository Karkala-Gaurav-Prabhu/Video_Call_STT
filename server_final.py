from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import struct

HOST = "192.168.1.105" #input("Enter Host IP: \n")
PORT_VIDEO = 3000
PORT_AUDIO = 4000
PORT_TEXT = 3005
lnF = 640 * 480 * 3
CHUNK = 1024
BufferSize = 4096
addressesAudio = {}
addressesText = {}
addresses = {}
threads = {}


def ConnectionsVideo():
    while True:
        try:
            clientVideo, addr = serverVideo.accept()
            print("{} video is connected!!".format(addr))
            addresses[clientVideo] = addr
            if len(addresses) > 1:
                for sockets in addresses:
                    if sockets not in threads:
                        threads[sockets] = True
                        sockets.send(("start").encode())
                        Thread(target=ClientConnectionVideo, args=(sockets,)).start()
            else:
                continue
        except:
            continue


def ConnectionsSound():
    while True:
        try:
            clientAudio, addr = serverAudio.accept()
            print("{} sound is connected!!".format(addr))
            addressesAudio[clientAudio] = addr
            Thread(target=ClientConnectionSound, args=(clientAudio,)).start()
        except:
            continue


def ConnectionsText():
    while True:
        try:
            clientText, addr = serverText.accept()
            print("{} text is connected!!".format(addr))
            addressesText[clientText] = addr
            Thread(target=ClientConnectionText, args=(clientText,)).start()
        except:
            continue

def ClientConnectionVideo(clientVideo):
    while True:
        try:
            lengthbuf = recvall(clientVideo, 4)
            length, = struct.unpack('!I', lengthbuf)
            recvall(clientVideo, length)
        except:
            continue


def ClientConnectionSound(clientAudio):
    while True:
        try:
            data = clientAudio.recv(BufferSize)
            broadcastSound(clientAudio, data)
        except:
            continue


def ClientConnectionText(clientText):
    while True:
        try:
            data = clientText.recv(BufferSize)
            broadcastText(clientText, data)
        except:
            continue

def recvall(clientVideo, BufferSize):
    databytes = b''
    i = 0
    while i != BufferSize:
        to_read = BufferSize - i
        if to_read > (1000 * CHUNK):
            databytes = clientVideo.recv(1000 * CHUNK)
            i += len(databytes)
            broadcastVideo(clientVideo, databytes)
        else:
            if BufferSize == 4:
                databytes += clientVideo.recv(to_read)
            else:
                databytes = clientVideo.recv(to_read)
            i += len(databytes)
            if BufferSize != 4:
                broadcastVideo(clientVideo, databytes)
    print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
    if BufferSize == 4:
        broadcastVideo(clientVideo, databytes)
        return databytes


def broadcastVideo(clientSocket, data_to_be_sent):
    for clientVideo in addresses:
        if clientVideo != clientSocket:
            clientVideo.sendall(data_to_be_sent)


def broadcastSound(clientSocket, data_to_be_sent):
    for clientAudio in addressesAudio:
        if clientAudio != clientSocket:
            clientAudio.sendall(data_to_be_sent)


def broadcastText(clientSocket, data_to_be_sent):
    for clientText in addressesText:
        if clientText != clientSocket:
            clientText.sendall(data_to_be_sent)


serverVideo = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverVideo.bind((HOST, PORT_VIDEO))
except OSError:
    print("Server Busy")

serverAudio = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverAudio.bind((HOST, PORT_AUDIO))
except OSError:
    print("Server Busy")

serverText = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverText.bind((HOST, PORT_TEXT))
except OSError:
    print("Server Busy")

serverAudio.listen(2)
print("Waiting for Audio connection..")
AcceptThreadAudio = Thread(target=ConnectionsSound)
AcceptThreadAudio.start()
#AcceptThreadAudio.join()
#serverAudio.close()

serverVideo.listen(2)
print("Waiting for Video connection..")
AcceptThreadVideo = Thread(target=ConnectionsVideo)
AcceptThreadVideo.start()
#AcceptThreadVideo.join()
#serverVideo.close()

serverText.listen(2)
print("Waiting for Text connection..")
AcceptThreadText = Thread(target=ConnectionsText)
AcceptThreadText.start()
AcceptThreadText.join()
serverText.close()