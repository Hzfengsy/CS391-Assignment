import socket
import sys
import os
import traceback
import threading
import select
import time

bind_host = ('0.0.0.0', 8080)
bind_num = 5

class HTTPRequestParser(object):
    def __init__(self, message):
        try:
            if isinstance(message, bytes):
                message = message.decode()
            command_line = message.split('\r\n')[0]
            self.command = command_line.split()[0]
            self.path = command_line.split()[1]
            self.request_version = command_line.split()[2]
            self.headers = {}
            lines = message.split('\r\n')[1:]
            headers = lines[:lines.index('')]
            for header in headers:
                header_item, header_data = header.split(': ', 1)
                self.headers[header_item.lower()] = header_data
        except:
            raise(Exception("Illegal HTTP Header"))

def https_proxy(connectionSocket, request, message, host, port=443):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the socket
        serverSocket.connect((host, port))
        connectionSocket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        http_epoll = select.epoll()
        # Create a temporary file on this socket and ask port 80 for the file requested by the client
        http_epoll.register(connectionSocket.fileno(), select.EPOLLIN)
        http_epoll.register(serverSocket.fileno(),  select.EPOLLOUT)
        serverBuff = []
        clientBuff = []
        while True:
            events = http_epoll.poll()
            for fileno, event in events:
                if event & select.EPOLLHUP:
                    http_epoll.close()
                    connectionSocket.close()
                    serverSocket.close()
                    return
                elif event & select.EPOLLIN:
                    if fileno == connectionSocket.fileno():
                        data = connectionSocket.recv(4096)
                        if data:
                            serverBuff.append(data)
                            http_epoll.modify(serverSocket.fileno(), select.EPOLLOUT)
                        else:
                            http_epoll.close()
                            connectionSocket.close()
                            serverSocket.close()
                            return
                    elif fileno == serverSocket.fileno():
                        data = serverSocket.recv(4096)
                        if data:
                            clientBuff.append(data)
                            http_epoll.modify(connectionSocket.fileno(), select.EPOLLOUT)
                        else:
                            http_epoll.close()
                            connectionSocket.close()
                            serverSocket.close()
                            return
                elif event & select.EPOLLOUT:
                    if fileno == connectionSocket.fileno():
                        for data in clientBuff:
                            connectionSocket.send(data)
                        clientBuff.clear()
                        http_epoll.modify(fileno, select.EPOLLIN)
                    elif fileno == serverSocket.fileno():
                        for data in serverBuff:
                            serverSocket.send(data)
                        serverBuff.clear()
                        http_epoll.modify(fileno, select.EPOLLIN)
    except:
        traceback.print_exc()
        print("Illegal request")
    finally:
        connectionSocket.close()

def http_proxy(connectionSocket, request, message, host, port=80):
    filename = request.path
    fileExist = False
    filetouse = filename.replace('/', ' ')
    try:
        # Check wether the file exist in the cache
        f = open('cache/' + filetouse, "r")
        outputdata = f.readlines()
        fileExist = True
        # ProxyServer finds a cache hit and generates a response message
        for line in outputdata:
            connectionSocket.send(line.encode())
        print('Read from cache')
    # Error handling for file not found in cache
    except IOError:
        if not fileExist:
            start_time = time.time()
            # Create a socket on the proxyserver
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            http_epoll = select.epoll()
            try:
                # Connect to the socket
                serverSocket.connect((host, port))
                http_epoll.register(connectionSocket.fileno(), select.EPOLLOUT)
                http_epoll.register(serverSocket.fileno(), select.EPOLLIN)
                serverSocket.send(message)
                serverBuff = []
                clientBuff = []
                while True:
                    events = http_epoll.poll()
                    for fileno, event in events:
                        if event & select.EPOLLHUP:
                            http_epoll.close()
                            connectionSocket.close()
                            serverSocket.close()
                            return
                        elif event & select.EPOLLIN:
                            if fileno == connectionSocket.fileno():
                                data = connectionSocket.recv(4096)
                                if data:
                                    serverBuff.append(data)
                                    http_epoll.modify(serverSocket.fileno(), select.EPOLLOUT)
                                else:
                                    http_epoll.close()
                                    connectionSocket.close()
                                    serverSocket.close()
                                    return
                            elif fileno == serverSocket.fileno():
                                data = serverSocket.recv(4096)
                                if data:
                                    clientBuff.append(data)
                                    http_epoll.modify(connectionSocket.fileno(), select.EPOLLOUT)
                                else:
                                    http_epoll.close()
                                    connectionSocket.close()
                                    serverSocket.close()
                                    return
                        elif event & select.EPOLLOUT:
                            if fileno == connectionSocket.fileno():
                                for data in clientBuff:
                                    connectionSocket.send(data)
                                clientBuff.clear()
                                http_epoll.modify(fileno, select.EPOLLIN)
                            elif fileno == serverSocket.fileno():
                                for data in serverBuff:
                                    serverSocket.send(data)
                                serverBuff.clear()
                                http_epoll.modify(fileno, select.EPOLLIN)
            except:
                traceback.print_exc()
                print("Illegal request")
        else:
            # HTTP response message for file not found
            with open('404.html') as f:
                connectionSocket.send(f.read())
    # Close the client and the server sockets
    connectionSocket.close()
    

if __name__ == '__main__':
    # Create a server socket, bind it to a port and start listening
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(bind_host)  
    serverSocket.listen(bind_num)

    if not os.path.exists('cache'):
        os.mkdir('cache')
    while True:
        # Strat receiving data from the client
        connectionSocket, addr = serverSocket.accept()
        print('Received a connection from:', addr)
        message = connectionSocket.recv(1024)
        try:
            request = HTTPRequestParser(message)
        except:
            continue
        host_prot = request.headers['host']
        if ':' in host_prot:
            host, port = host_prot.split(':')
            port = int(port)
        else:
            host = host_prot
            port = 80
        print(host, port)
        if request.command == 'CONNECT':
            thread = threading.Thread(target=https_proxy, args=(connectionSocket, request, message, host, port))
            thread.start()
        else:
            thread = threading.Thread(target=http_proxy, args=(connectionSocket, request, message, host, port))
            thread.start()
    serverSocket.close()