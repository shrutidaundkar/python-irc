import threading
import socket
import sys

#BELOW CODE IS TO SEND AND WRITE THE MESSAGES
def getFromServer():
    while True:
        try:
            message = clientConn.recv(1024).decode('utf-8')
            
            #GETTING USER NAME
            if message == 'GetUserName':
                clientConn.send(clientName.encode('utf-8'))
            
            #EXITTING
            elif message == 'exit':
                sys.exit(-1)
            
            #GET ROOM NAMES
            elif message == 'GetRoomNames':
                rooms=''
                rooms=input('Enter room names:')
                clientConn.send(rooms.encode('utf-8'))
            
                
            else:
                print(message,'\n')
        
        except Exception as e:
            print('Server not responding',e.args)
            clientConn.close()
            sys.exit(-1)

def sendtoServer():
    while True:
        message = '{} {}'.format(clientName, input(''))
        try:
            clientConn.send(message.encode('utf-8'))
        except:
            sys.exit(-1)
            
#CLIENT START
clientName = input("Enter your name: ")
threadLists = []

#STARTING THE CONNECTION
clientConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientConn.connect(('127.0.0.1', 50505))

#STARTING THREAD FOR GETTING INFO FROM SERVER
getServerThread = threading.Thread(target=getFromServer)
getServerThread.start()
threadLists.append(getServerThread)

#STARTING THREAD FOR SENDING MESSAGES FROM SERVER
sendThread = threading.Thread(target=sendtoServer)
sendThread.start()
threadLists.append(sendThread)
