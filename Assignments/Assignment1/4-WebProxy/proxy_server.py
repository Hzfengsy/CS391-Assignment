# This proxy support HTTP and also HTTPS.
# Because of TLS/SSL protocol, it is impossible to read messages or cache data in HTTPS connection
# This proxy server can only run on Linux 2.5+ system
import socket
import os
import threading
import select
import hashlib
import traceback

bind_host = ('0.0.0.0', 8080)
bind_num = 20

# A HTTP request header parser.
# Provide some simple API which is same as BaseHTTPRequestHandler in Python2.
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

def forwardMsg(clientSocket, serverSocket, initMsg=[], cache=False, bufferSize=4096):

    # Close all connection
    def _closeConnection(epoll, clientSocket, serverSocket):
        epoll.close()
        clientSocket.close()
        serverSocket.close()

    # Check whether a file has been cached or can be cached.
    # Return Format:
    #     return a tuple with two elements (_valid, _file)
    #     _valid will be True if the request has been cached, otherwise, False.
    #     _file will be a file object if the request has been cached or can be cached. Otherwise, None.
    def _checkCacheFile(message_list):
        message = b''
        for msg in message_list:
            message += msg
        request = HTTPRequestParser(message)

        # Only cache request with method GET.
        if request.command == 'GET':
            # Hash the message with MD5 algorithm.
            # Only when hole request messages are same can be recognized as the same request.
            hash = hashlib.md5()
            hash.update(message)
            filename = 'cache/' + hash.hexdigest()
            if os.path.exists(filename):
                return True, open(filename, 'rb')
            else:
                return False, open(filename, 'wb')
        else:
            return False, None

    # Create a epoll object to efficiently solve I/O multiplexing problem.
    http_epoll = select.epoll()
    # Register client to read event.
    http_epoll.register(clientSocket.fileno(), select.EPOLLIN)
    # Register server to write event.
    http_epoll.register(serverSocket.fileno(), select.EPOLLOUT)

    opposites = {serverSocket.fileno(): clientSocket.fileno(), clientSocket.fileno(): serverSocket.fileno()}
    sockets = {serverSocket.fileno(): serverSocket, clientSocket.fileno(): clientSocket}
    buff = {serverSocket.fileno(): initMsg, clientSocket.fileno(): []}
    cacheFile = None

    try:
        while True:
            # Catch the socket events.
            events = http_epoll.poll()
            for fileno, event in events:
                if event & select.EPOLLHUP:
                    # Finish caching when socket closed.
                    if cache and cacheFile != None:
                        cacheFile.close()
                        cacheFile = None
                    # Close connection when socket hanged up.
                    _closeConnection(http_epoll, clientSocket, serverSocket)
                    return
                elif event & select.EPOLLIN:
                    # Socket is now available for reading.
                    data = sockets[fileno].recv(bufferSize)
                    if data:
                        # Append data to sending buffer of the other socket.
                        buff[opposites[fileno]].append(data)
                        # The other socket is now ready to send message and register the event.
                        http_epoll.modify(opposites[fileno], select.EPOLLOUT)
                        # Finish caching when there is another request sent from browser.
                        if cache and cacheFile != None and fileno == clientSocket.fileno():
                            cacheFile.close()
                            cacheFile = None
                        # Cache the data from remote server if a file is being cached.
                        elif cache and cacheFile != None and fileno == serverSocket.fileno():
                            cacheFile.write(data)
                    else:
                        # Finish caching when socket closed.
                        if cache and cacheFile != None and fileno == serverSocket.fileno():
                            cacheFile.close()
                            cacheFile = None
                        # Close connection when socket closed by remote.
                        _closeConnection(http_epoll, clientSocket, serverSocket)
                        return
                elif event & select.EPOLLOUT:
                    # Socket is now available for writing.
                    # Check weather the request has been cached or can be cached before sending to the server.
                    if cache and fileno == serverSocket.fileno():
                        valid, file = _checkCacheFile(buff[fileno])
                        if valid:
                            # The request has been cached, respond to the browser immediately.
                            buff[opposites[fileno]].append(file.read())
                            # Clean the sending buffer.
                            buff[fileno].clear()
                            # Clean events between proxy and server.
                            http_epoll.modify(fileno, 0)
                            # The socket to the browser is now ready to send message and register the event.
                            http_epoll.modify(opposites[fileno], select.EPOLLOUT)
                            print('read from cache')
                            # Prevent request from sending to server.
                            continue
                        else:
                            # The request is being cached.
                            cacheFile = file

                    # Forward message to the other side.
                    for data in buff[fileno]:
                       sockets[fileno].send(data)
                    # Clean the sending buffer.
                    buff[fileno].clear()
                    # The socket is now ready to receive message and register the event.
                    http_epoll.modify(fileno, select.EPOLLIN)
    except BrokenPipeError:
        # Socket closed by browser unexpected.
        print("connection closed by remote server")
    finally:
        _closeConnection(http_epoll, clientSocket, serverSocket)

def httpsProxy(connectionSocket, message, host, port=443):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the socket.
        serverSocket.connect((host, port))
        # Parse the header and get request version.
        request = HTTPRequestParser(message)
        # Send response to browser.
        connectionSocket.send("{} 200 Connection Established\r\n\r\n".format(request.request_version).encode())
        # Forward message to the server.
        forwardMsg(connectionSocket, serverSocket)
    except:
        traceback.print_exc()
        print("Illegal request")

def httpProxy(connectionSocket, message, host, port=80):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to the socket.
        serverSocket.connect((host, port))
        # Forward message and cache files.
        forwardMsg(connectionSocket, serverSocket, initMsg=[message], cache=True)
    except:
        traceback.print_exc()
        print("Illegal request")

def proxyServe(serverSocket):
    while True:
        # Strat receiving data from the client.
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024)

        try:
            # Try to Parse HTTP header.
            request = HTTPRequestParser(message)
        except Exception as e:
            # Omit the request if it is illegal.
            print(str(e))
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
            thread = threading.Thread(target=httpsProxy, args=(connectionSocket, message, host, port))
            thread.start()
        else:
            thread = threading.Thread(target=httpProxy, args=(connectionSocket, message, host, port))
            thread.start()

if __name__ == '__main__':
    # Create a server socket, bind it to a port and start listening.
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind(bind_host)  
    serverSocket.listen(bind_num)

    # Make directory to store cache file.
    if not os.path.exists('cache'):
        os.mkdir('cache')

    try:
        proxyServe(serverSocket)
    except KeyboardInterrupt:
        serverSocket.close()