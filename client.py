from socket import AF_INET, SOCK_STREAM, socket
import speech_recognition as sr
from tkinter import *
from threading import Thread

HOST = '192.168.1.105'
PORT = 3000
BufferSize = 1024
root = Tk()


def Recieve():
    while True:
        try:
            msg = client.recv(BufferSize).decode("utf-8")
            cm = Label(root, text=msg)
            cm.pack(fill=X)
        except OSError:
            break


def Send():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            audio1 = r.listen(source)
        try:
            query = r.recognize_google(audio1, language='en-in')
            client.send(query.encode("utf-8"))
            print('sent')

        except sr.UnknownValueError:
            print('Sorry! Please Repeat!')
            Send()


client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

RecieveThread = Thread(target=Recieve).start()
SendThread = Thread(target=Send).start()
Thread1 = Thread(target=root.mainloop()).start()
