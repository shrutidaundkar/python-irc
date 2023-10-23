
#IMPORT STATEMENTS
import socket
import threading

#USER CLASS DEFINITION
class User:
    def __init__(self, name):
        self.name = name
        self.allJoinedRooms = []
        self.thisRoom = ''

#ROOM CLASS DEFINITION
class Room:
    def __init__(self, name):
        self.allACientConnections = []
        self.allClientNames = []
        self.roomName = name

#LISTING ALL ROOMS WITH MEMBERS 
def listRoomsWithMembers(nickname):
    name = allClientConns[nickname]
    print(len(allRoomsDictionary))
    if len(allRoomsDictionary) == 0:
        name.send('No rooms have been created'.encode('utf-8'))
    else:
        reply = "\n----------------------\nRooms with members:\n----------------------"
        for room in allRoomsDictionary:
            reply += '\nRoom Name: '+ allRoomsDictionary[room].roomName +'\nMembers:'
            for people in allRoomsDictionary[room].allClientNames:
                reply += '\n'+ people  
            reply += '\n----------------------\n'
        name.send(f'{reply}'.encode('utf-8'))

#LISTING ALL ROOMS
def listAllRooms(userName):
    clientConn = allClientConns[userName]
    reply = "\n----------------------\nList of rooms:\n----------------------"
    for room in allRoomsDictionary:
        print(allRoomsDictionary[room].roomName)
        reply += '\n'+ allRoomsDictionary[room].roomName
        print(allRoomsDictionary[room].allClientNames)
    reply += '\n----------------------'
    clientConn.send(f'{reply}'.encode('utf-8'))

#LISTING ALL CLIENTS
def listAllClients(userName):
    clientConn = allClientConns[userName]
    reply = "\n----------------------\nList of Users:\n----------------------"
    for client in clientNamesList:
        reply += '\n'+ str(client)
    reply += '\n----------------------'
    clientConn.send(f'{reply}'.encode('utf-8'))
    
#JOINING OR CREATING NEW ROOM IF DOES NOT EXISTS
def joinOrCreateRoomIfNotExist(nickname, room_name):
    name = allClientConns[nickname]
    user = allClientUserObjects[nickname]
    if len(room_name) == 0:
        name.send('Room name cannot be empty. Enter a valid name')
    elif room_name not in allRoomsDictionary:
        room = Room(room_name)
        allRoomsDictionary[room_name] = room
        room.allACientConnections.append(name)
        room.allClientNames.append(nickname)

        user.thisRoom = room_name
        user.allJoinedRooms.append(room)
        name.send(f'{room_name} created'.encode('utf-8'))
    else:
        room = allRoomsDictionary[room_name]
        if room_name in user.allJoinedRooms:
            name.send('You are already in the room'.encode('utf-8'))
        else:
            room.allACientConnections.append(name)
            room.allClientNames.append(nickname)
            user.thisRoom = room_name
            user.allJoinedRooms.append(room)
            sendMessageToRoom(f'{nickname} joined the room', room_name)

#SWITICHING ROOMS           
def switchToRoom(nickname, roomname):
    user = allClientUserObjects[nickname]
    name = allClientConns[nickname]
    room = allRoomsDictionary[roomname]
    if roomname == user.thisRoom:
        name.send('You are already in the room'.encode('utf-8'))
    elif room not in user.allJoinedRooms:
        name.send('Switch not available, you are not part of the room'.encode('utf-8'))
    else:
        user.thisRoom = roomname
        name.send(f'Switched to {roomname}'.encode('utf-8'))

#LEAVING CURRENTLY JOINED ROOM
def leaveRoom(nickname):
    user = allClientUserObjects[nickname]
    name = allClientConns[nickname]
    if user.thisRoom == '':
        name.send('You are not part of any room'.encode('utf-8'))
    else:
        roomname = user.thisRoom
        room = allRoomsDictionary[roomname]
        user.thisRoom = ''
        user.allJoinedRooms.remove(room)
        allRoomsDictionary[roomname].allACientConnections.remove(name)
        allRoomsDictionary[roomname].allClientNames.remove(nickname)
        sendMessageToRoom(f'{nickname} left the room', roomname)
        name.send('You left the room'.encode('utf-8'))


#SENDING PRIVATE MESSAGE TO OTHER USER
def sendPrivateMessage(message):
    args = message.split(" ")
    user = args[2]
    sender = allClientConns[args[0]]
    if user not in allClientConns:
        sender.send('User not found'.encode('utf-8'))
    else:
        reciever = allClientConns[user]
        msg = ' '.join(args[3:])
        reciever.send(f'[personal message] {args[0]}: {msg}'.encode('utf-8'))
        sender.send(f'[personal message] {args[0]}: {msg}'.encode('utf-8'))

#REMOVING CLIENT FROM SERVER
def removingClient(nickname):
    clientNamesList.remove(nickname)
    client = allClientConns[nickname]
    user = allClientUserObjects[nickname]
    user.thisRoom = ''
    for room in user.allJoinedRooms:
        room.allACientConnections.remove(client)
        room.allClientNames.remove(nickname)
        sendMessageToRoom(f'{nickname} left the room', room.roomName)

#SENDING MESSAGE IN A ROOM 
def sendMessageToRoom(message, ROOM_NAME):
    for client in allRoomsDictionary[ROOM_NAME].allACientConnections:
        msg = '['+ROOM_NAME+'] '+' '+ message
        client.send(msg.encode('utf-8'))

#BROADCAST TO ALL
def broadcastMessageFromClient(nick,message):
    message = '[Broadcast from '+nick+'] '+ " ".join(message[1:])
    for client in clientConnList:
        client.send(str(message).encode('utf-8')) 
        
#TO PARSE THE USER COMMANDS
def clientCommands(client):
    clientName=''
    while True:
        try:
            #GETTING USER COMMAND
            userCommand = client.recv(1024).decode('utf-8')
            userCommandArray = userCommand.split(" ")
            clientConn = allClientConns[userCommandArray[0]]
            clientName = userCommandArray[0]
            
            #PARSING USER COMMAND 

            #LISTING ROOMS/USERS
            if '#0' in userCommand:
                listAllRooms(clientName)
                listAllClients(clientName)
                
            #LISTING ROOMS WITH USERS CASE
            elif '#1' in userCommand:
                listRoomsWithMembers(userCommandArray[0])
                
            #JOINING ROOM IF EXISTS OR CREATE NEW IF DOESN'T EXISTS    
            elif '#2' in userCommand:
                joinOrCreateRoomIfNotExist(userCommandArray[0], ' '.join(userCommandArray[2:]))
            
            #SWITCHING ROOM CASE    
            elif '#3' in userCommand:
                switchToRoom(userCommandArray[0], userCommandArray[2])
            
            #LEAVE CURRENT ROOM CASE    
            elif '#4' in userCommand:
                leaveRoom(userCommandArray[0])
            
            #SENDING PRIVATE MESSAGE TO OTHER CLIENT CASE    
            elif '#5' in userCommand:
                sendPrivateMessage(userCommand)  
            
            #MESSAGE TO SELECTED ROOMS CASE      
            elif '#6' in userCommand:
                clientConn.send('GetRoomNames'.encode('utf-8'))
                selectedRooms= clientConn.recv(1024).decode('utf-8')
                selectedRooms= selectedRooms.strip().split(' ')
                msg = ' '.join(userCommandArray[1:])
                for room in selectedRooms:
                    sendMessageToRoom(''.join(userCommandArray[1:]),room)
            
            #BROADCAST TO EVERY CLIENT CASE        
            elif '#7' in userCommand:    
                broadcastMessageFromClient(clientName,userCommandArray[1:])     
            
            #RE-PRINT MENU      
            elif '#8' in userCommand:    
                clientConn.send(mainMenu.encode('utf-8'))
            
            #EXIT CASE    
            elif '#9' in userCommand:
                clientConn.send('exit'.encode('utf-8'))
                clientConn.close()
               
            #DEFAULT CASE                
            else:
                if allClientUserObjects[userCommandArray[0]].thisRoom == '':
                    clientConn.send('Please join a room to send messages.'.encode('utf-8'))
                else:
                    msg = ' '.join(userCommandArray[1:])
                    room = allClientUserObjects[userCommandArray[0]].thisRoom
                    sendMessageToRoom(f'[{userCommandArray[0]}] {msg}',room)
        
        #EXCEPTION HANDLING            
        except Exception as e:
            print("Exception occured:", e)
            clientConnList.remove(client)
            clientConn.close()
            print(f'{clientName} left the room\n')
            if clientName in clientNamesList:
                removingClient(clientName)
            break

#server main
def acceptClients():
    
    while True:
        try:
            #ACCEPTING CLIENT CONNECTIONS
            clientConn, clientAddress = server.accept()
            
            #GETTING CLIENT NAME
            clientConn.send('GetUserName'.encode('utf-8'))
            username = clientConn.recv(1024).decode('utf-8')
            
            #ADDING CLIENT NAME TO CLIENT LIST
            clientNamesList.append(username)
            clientConnList.append(clientConn)
            
            #STORING USER OBJECT AND CONNECTION OBJECT FOR FUTURE USE
            allClientUserObjects[username] = User(username)
            allClientConns[username] = clientConn
            
            print(f'\nClient connected on {clientAddress} with username:{username}')
            clientConn.send(f'Hi {username}! You have successfully connected to the server!\n'.encode('utf-8'))
            clientConn.send(mainMenu.encode('utf-8'))
            
            #Assigning a separate thread for each client
            clientThread = threading.Thread(target=clientCommands, args=(clientConn,))
            clientThread.start()
            
        except Exception as e:
            print('Exception occured: '+e)


#**********************************************************************************************************
#STARTING, BINDING AND LISTENING THE SERVER SOCKET FOR IPv4 ADDRESSES AND TCP CONNNECTION
#**********************************************************************************************************
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 50505))
server.listen()

#**********************************************************************************************************
# INITIALIZING EMPTY LISTS AND MENU STRING
#**********************************************************************************************************
clientConnList = []     #CLIENT SOCKET LIST
clientNamesList = []    #CLIENT NAMES LIST
allRoomsDictionary = {}  #ROOM OBJECTS ARRAY
allClientConns = {}     #ALL CLIENT CONNECTION OBJECTS
allClientUserObjects = {}  #ALL CLIENT(USER) OBJECTS

mainMenu =  """ 
                               
******************************  MENU  **********************************************
No.  Functionality                                    Command
************************************************************************************
0.   To list all the available rooms and clients      #0 
1.   To list rooms with members                       #1
2.   To join or create the room if does not exist     #2 room_name 
3.   To switch room                                   #3 new_room_name 
4.   To leave current room                            #4 
5.   To send a direct personal message                #5 receiver_username message
6.   To send a direct message to specified rooms      #6 message
7.   To broadcast message to everyone                 #7 message
8.   To print menu again                              #8
9.   To exit IRC                                      #9
Or enter message to send in current Room: """

               
print('\nServer Started at port: 50505 \n')
acceptClients()

