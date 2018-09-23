#import socket module
from socket import *
import threading

serverSocket = socket(AF_INET, SOCK_STREAM)
#Prepare a sever socket
serverSocket.bind(('0.0.0.0', 8080))
serverSocket.listen(10)

def serve(connectionSocket, addr):
    try:
        message = connectionSocket.recv(1024)
        if message.strip != '': 
            filename = message.split()[1]
            f = open(filename[1:])
            outputdata = f.read().split('\n')
            #Send one HTTP header line into socket
            connectionSocket.send('HTTP/1.1 200 OK\n\n')
            #Send the content of the requested file to the client
            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i])
        connectionSocket.close()
    except IOError as e:
        #Send response message for file not found
        outputdata = 'HTTP/1.1 404 Not Found\n\n'
        connectionSocket.send(outputdata)
        #Close client socket
        connectionSocket.close()

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    thread = threading.Thread(target=serve, args=(connectionSocket, addr))
    thread.start()

serverSocket.close() 