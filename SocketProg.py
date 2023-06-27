from socket import *##for socketing
from hashlib import sha1##for hashing
import struct ##for decoding
from tkinter import *##for simple ui
from multiprocessing import Process##for multiprocessing input and output seperately (server client)
import threading##for keeping the output UI seperate from the server messages.

## Made in Python 3.8.10, doesn't work with newer versions of python.
##start button is at outputs of the game window
## Mehmet Utku Ozhun 150170018 Computer Communications Assignment1 

def Initialize():
    ########################
    #Creating Socket
    #####################
    serverName = 'IPOFSERVER'
    serverPort = 2022
    global clientSocket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    ##################
    #socket created
    ################
    #sending data
    #################
    print("connection done")
    sentence = "Start_Connection"
    clientSocket.send(sentence.encode())
    print("sentence sent")
    #####################
    #Data Sent
    ###############
    #Receiveing data
    ############
    randomHex = clientSocket.recv(2022)
    print(randomHex)
    ################
    #Data Recieved
    ###############
    #Combining data with my hexkey
    #######################3
    hex64 = randomHex.decode() + "B8F43AC9EF6D0FE93BF34D6AF98B87FE"
    print(len(hex64))
    ##########
    #hashing
    #########
    sha1x = sha1()
    sha1x.update(hex64.encode())
    sha1x.digest()
    sha1result = sha1x.hexdigest()
    print(len(sha1result))
    ###################
    #hashing done
    ##################
    chararray =  sha1result+ '#' + "150170018"
    print(chararray)
    #############
    #send auth info
    ###########
    clientSocket.send(chararray.encode())
    print("message sent")
    message = clientSocket.recv(2022)
    print(message.decode())
    clientSocket.send(
        struct.pack('B', 0)
    )
    message = clientSocket.recv(2022)
    print(message.decode())
    clientSocket.send(
        struct.pack('B', 2)
    )
    #################
    #auth info sent and got authentication
    ######################





##basic output UI 
def outputs():
    opwindow = Tk()
    opwindow.title("Outputs of game")
    global remainingtime
    remainingtime = Text()
    remainingtime.config(height=1, width=4)
    remainingtime.tag_add('time', '1.0', 'end')
    start = Button(opwindow, text="start", command=startLoop)
    remainingtime.pack()
    start.pack()
    global dialogue
    dialogue = Text()
    dialogue.config(height=50, width=100)
    dialogue.pack()
    dialogue.insert('1.0', "Hello, start button is at the bottom of this window")
    
    opwindow.mainloop()
    
##target threading
def startLoop():
    threading.Thread(target=startLoopThread).start()


##the thread keeps looping and gets messages. Depending on the message received, does different things.
def startLoopThread():
    while True:
        message = clientSocket.recv(2022)
        #print(message.decode())
        if(message[0] == 0):
            newmes = decodeInfo(message)
            dialogue.insert('end', '\n')
            dialogue.insert('end', newmes)
            print(newmes)
        elif(message[0] == 1):
            newmes = decodeInfoQuestion(message)
            dialogue.insert('end', '\n')
            dialogue.insert('end', newmes)
            print(message)
        elif(message[0] == 3):
            time = message[5] * 255 + message[4]
            remainingtime.delete('1.0', 'end')
            remainingtime.insert('1.0', str(time))
            print(time)
        elif(message[0] == 2):
            dialogue.insert('end', '\n')
            print(message)
            dialogue.insert('end', "Pos of letter: ")
            dialogue.insert('end', message[2])
            dialogue.insert('end', "\n letter: ")
            letter = chr(message[3])
            dialogue.insert('end', letter)
        elif(message[0] == 4):
            print("ENDGAME")
            print(message)
            score = message[3] * 255 + message[2] 
            remtime = message[5] * 255 + message[4]
            dialogue.insert('end', '\n')
            dialogue.insert('end', "Game ended \nTotal Score: ")
            dialogue.insert('end', score)
            dialogue.insert('end', "\nRemaining Time")
            dialogue.insert('end', remtime)
            break



def decodeInfo(byteInfo:bytes):
    Encoding_type = byteInfo[1]
    if(Encoding_type == 1):
        sizeOfPayload = getsizeofpayload(byteInfo)
        message = byteInfo[4:]#if its utf16, payloadsize doubles
        message = message.decode('utf16')
        message = "Information! \n" + message
        return message
    elif(Encoding_type == 0):
        sizeOfPayload = getsizeofpayload(byteInfo)
        message = byteInfo[4:]#starts from 4 since [0,1,2,3] [packtype,enctype,sizepay1,sizepay2]
        message = message.decode()
        message = "Information! \n" + message
        return message



#############################
#on information and question messages, depending on the encoding type, returns the decoded string value.
#############################
def decodeInfoQuestion(byteInfo: bytes):
    Encoding_type = byteInfo[1]
    if(Encoding_type == 1):
        sizeOfPayload = getsizeofpayload(byteInfo)
        lengthofword = byteInfo[4] + byteInfo[5]*255
        message = byteInfo[6:6+sizeOfPayload*2]#if its utf16, payloadsize doubles
        message = message.decode('utf16')
        message = "Length of word = " + str(lengthofword) +"\n Hint:  "+ message
        return message
    elif(Encoding_type == 0):
        sizeOfPayload = getsizeofpayload(byteInfo)
        lengthofword = byteInfo[4] + byteInfo[5]*255
        message = byteInfo[6:]#starts from 6 since [0,1,2,3,4,5] [packtype,enctype,sizepay1,sizepay2,length1,length2]
        message = message.decode()
        message = "Length of word = " + str(lengthofword) +"\n Hint:  "+ message
        return message


################################
#returns sizeof payload.
#################################
def getsizeofpayload(byteInfo:bytes):
    sizeOfPayload = byteInfo[2] + byteInfo[3] * 255
    return sizeOfPayload


        
######################################
#Functions below are for the input UI Panel
######################################

def submitText():
    answer = entry.get()
    clientSocket.send(
        struct.pack('B', 4)
        +
        answer.encode()
    )
    
def fetchQuestion():
    clientSocket.send(
        struct.pack('B', 2)
    )

def getRemTime():
    clientSocket.send(
        struct.pack('B', 5)
    )

def buyALetter():
    clientSocket.send(
        struct.pack('B', 3)
    )

def terminateTheGame():
    clientSocket.send(
        struct.pack('B', 1)
    )

############################
#Using Tkinter for a simple interface for inputs
############################
def inputsGUI():
    ipwindow = Tk()
    ipwindow.title("Inputs of game")
    submit = Button(ipwindow, text="submit", command=submitText)
    fetch = Button(ipwindow, text="fetch", command=fetchQuestion)
    buyaLetter = Button(ipwindow, text="buy a letter", command=buyALetter)
    getremTime = Button(ipwindow, text="GetRemTime", command=getRemTime)
    terminateGame = Button(ipwindow, text="TerminateGame", command=terminateTheGame)
    global entry
    entry = Entry()
    entry.config(font=('Times New Roman', 40))
    entry.pack()
    submit.pack()
    fetch.pack()
    buyaLetter.pack()
    getremTime.pack()
    terminateGame.pack()
    ipwindow.mainloop()



if __name__ == "__main__":
    opaccessed = False
    Initialize()
    #processes
    procs = []
    proc1 = Process(target=outputs)
    proc2 = Process(target=inputsGUI)
    proc1.start()
    proc2.start()
    proc2.join()
    proc1.join()








