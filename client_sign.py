from tkinter import *
import cv2
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from imutils.video import WebcamVideoStream
import tensorflow.keras
from PIL import Image, ImageOps
import speech_recognition as sr
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct

np.set_printoptions(suppress=True)

# Load the model
model = tensorflow.keras.models.load_model('keras_model.h5')

norm_data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

text = ""
HOST = "192.168.1.105"
PORT_VIDEO = 3000
PORT_AUDIO = 4000
PORT_TEXT = 3005
BufferSize = 4096
CHUNK = 1024
lnF = 640 * 480 * 3
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
BUFFER_SIZE_TEXT = 1024

root = Tk()
root.title("Video Call Application")
root.geometry("1220x692+60+2")
app = Frame(root)
app.grid()

C = Canvas(root, bg="blue", height=250, width=300)
filename = PhotoImage(file = r"C:\Users\gaura\PycharmProjects\AllSense\Home_Video.png")
background_label = Label(root, image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT_TEXT))


clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientVideoSocket.connect((HOST, PORT_VIDEO))
wvs = WebcamVideoStream(0).start()

clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientAudioSocket.connect((HOST, PORT_AUDIO))

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)
initiation = clientVideoSocket.recv(5).decode()

def translation(img) :
    text1 = ""
    img = cv2.resize(img, (224, 224))

    # turn the image into a numpy array
    image_array = np.asarray(img)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    # Load the image into the array
    norm_data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(norm_data)
    # print(prediction)
    for i in prediction:
        if i[0] > 0.7:
            text1 = "Hello"
        if i[1] > 0.7:
            text1 = "No"
        if i[2] > 0.7:
            text1 = "Yes"
        if i[3] > 0.7:
            text1 = "ok"
        if i[4] > 0.7:
            text1 = "Thank you!"
    print(text1)
    return text

def start_video() :
    if initiation == "start":
        SendFrameThread = Thread(target=SendFrame).start()
        SendAudioThread = Thread(target=SendAudio).start()
        SendThread = Thread(target=Send).start()
        RecieveFrameThread = Thread(target=RecieveFrame).start()
        RecieveAudioThread = Thread(target=RecieveAudio).start()
        RecieveThread = Thread(target=Recieve).start()

def SendAudio():
    while True:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if (vol > 500):
            #print("Recording Sound...")
            pass
        else:
            #print("Silence..")
            pass
        clientAudioSocket.sendall(data)


def RecieveAudio():
    while True:
        data = recvallAudio(BufferSize)
        stream.write(data)


def recvallAudio(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += clientAudioSocket.recv(4 * CHUNK)
        else:
            databytes += clientAudioSocket.recv(to_read)
    return databytes


def SendFrame():
    while True:
        try:
            frame = wvs.read()
            text = translation(frame)
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            frame = np.array(frame, dtype=np.uint8).reshape(1, lnF)
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 1)
            jpg_as_text = bytearray(frame)

            databytes = zlib.compress(jpg_as_text, 9)
            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            clientVideoSocket.sendall(length)
            while len(databytes) > 0:
                if (5000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(5000 * CHUNK)]
                    databytes = databytes[(5000 * CHUNK):]
                    clientVideoSocket.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket.sendall(bytesToBeSend)
                    databytes = b''
            #print("##### Data Sent!! #####")
        except:
            continue


def RecieveFrame():
    while True:
        try:
            lengthbuf = recvallVideo(4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvallVideo(length)
            img = zlib.decompress(databytes)
            if len(databytes) == length:
                #print("Recieving Media..")
                #print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))
                img = np.array(img, dtype=np.uint8).reshape(480, 640, 3)
                cv2.imshow("Stream", img)
                cv2.namedWindow("Stream")
                cv2.moveWindow("Stream", 580, 139)
                if cv2.waitKey(1) == 27 :
                    cv2.destroyAllWindows()
            else:
                print("Data CORRUPTED")
        except:
            continue


def recvallVideo(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (5000 * CHUNK):
            databytes += clientVideoSocket.recv(5000 * CHUNK)
        else:
            databytes += clientVideoSocket.recv(to_read)
    return databytes


def Send():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            #print("Listening...")
            r.pause_threshold = 1
            audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language='en-in')
            print(f"Sending {query}")
            client.send(query.encode("utf-8"))

        except sr.UnknownValueError:
            #print('Sorry! Please Repeat!')
            Send()


def Recieve():
    while True:
        try:
            msg = client.recv(BUFFER_SIZE_TEXT).decode("utf-8")
            print(f"Recieving {msg}")
            cm = Label(root, text=msg).place(x=62, y=250)
            #cm.grid()
        except OSError:
            break

home_exit = Button(root, text = "EXIT",height = "1", width = "15", command = root.destroy).place(x=1090, y=658) #Home screen exit button
connect_btn = Button(root, text = "CONNECT",height = "1", width = "61", command = start_video).place(x=62, y=330)

root.mainloop()