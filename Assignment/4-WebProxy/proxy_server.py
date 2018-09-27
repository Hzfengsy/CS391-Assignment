from socket import *
import sys
import os

# Create a server socket, bind it to a port and start listening
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('0.0.0.0', 8080))
serverSocket.listen(10)
if not os.path.exists('cache'):
    os.mkdir('cache')
    
while True:
    # Strat receiving data from the client
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    print('Received a connection from:', addr)
    message = connectionSocket.recv(1024)
    # Extract the filename from the given message
    filename = str(message).split()[1].partition("/")[2]
    fileExist = False
    filetouse = "/" + filename
    print(filetouse)
    try:
        # Check wether the file exist in the cache
        f = open('cache/' + filetouse[1:], "r")
        outputdata = f.readlines()
        fileExist = True
        # ProxyServer finds a cache hit and generates a response message
        connectionSocket.send("HTTP/1.1 200 OK\r\n")
        connectionSocket.send("Content-Type:text/html\r\n\r\n")
        for line in outputdata:
            connectionSocket.send(line)
        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if not fileExist:
            # Create a socket on the proxyserver
            clientSocket = socket(AF_INET, SOCK_STREAM)
            hostn = filename.split('/')[0]
            print(hostn)
            try:
                # Connect to the socket to port 80
                clientSocket.connect((hostn, 80))
                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                fileobj = clientSocket.makefile('rw', 0)
                fileobj.write("GET "+"http://" + filename + "HTTP/1.1\r\n\r\n")
                # Read the response into buffer
                buff = fileobj.readlines()
                # Create a new file in the cache for the requested file.
                filename = "cache/" + filename
                # path = '/'.join(filename.split('/')[:-1])
                # os.makedirs(path)
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                tmpFile = open(filename,"wb")
                for line in outputdata:
                    connectionSocket.send(line)
                    tmpFile.write(line)
            except Exception as e:
                print(str(e))
                print("Illegal request")
        else:
            # HTTP response message for file not found
            outputdata = 'HTTP/1.1 404 Not Found\r\n\r\n'
            with open('404.html') as f:
                connectionSocket.send(f.read())
    # Close the client and the server sockets
    connectionSocket.close()

serverSocket.close()