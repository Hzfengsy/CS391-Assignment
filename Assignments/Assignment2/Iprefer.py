import socket
import sys
import time
import argparse

class Client(object):

    def __init__(self, serverName, serverPort, time):
        self.serverName = serverName
        self.serverPort = serverPort
        self.time = time

    def sendData(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bytesSent = 0
        try:
            clientSocket.connect((self.serverName, self.serverPort))
        except:
            print("Error: cannot connect to server.")
            sys.exit(1)

        data = bytearray(1000)
        start = time.time()
        current = time.time()
        while current - start < self.time:
            clientSocket.send(data)
            bytesSent += len(data)
            current = time.time()
        
        clientSocket.close()

        rate = 8.0 * bytesSent / (current - start) / 1000 / 1000
        print("sent=%d KB rate=%.3f Mbps" % (bytesSent / 1000, rate))


class Server(object):
    def __init__(self, serverPort):
        self.serverPort = serverPort
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('0.0.0.0', self.serverPort))
        self.serverSocket.listen(10)
    
    def listen(self):
        while True:
            connectionSocket, addr = self.serverSocket.accept()
            firstMoment = time.time()
            data = connectionSocket.recv(1024)
            bytesReceived = 0
            while data:
                bytesReceived += len(data)
                data = connectionSocket.recv(1024)
            lastMoment = time.time()

            rate = 8.0 * bytesReceived / (lastMoment - firstMoment) / 1000 / 1000
            print("sent=%d KB rate=%.3f Mbps" % (bytesReceived / 1000, rate))

def validPort(port):
    return 1024 <= port and port <= 65535

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-c","--client", help="launch as a client", action="store_true")
    parser.add_argument("-s","--server", help="launch as a client", action="store_true")
    parser.add_argument("-h","--host", help="the host of connect", type=str)
    parser.add_argument("-p","--port", help="the connection port", type=int)
    parser.add_argument("-t","--time", help="the connection time", type=int)
    args = parser.parse_args()
    if args.client and args.server:
        print("Error: Cannot run the program in both client and server mode.")
        sys.exit(1)

    if not args.client and not args.server:
        print("Error: Designation either client or server mode.")
        sys.exit(1)

    if args.client:
        if args.host and args.port and args.time:
            if not validPort(args.port):
                print("Error: port number must be in the range 1024 to 65535.")
                sys.exit(1)
            client = Client(args.host, args.port, args.time)
            client.sendData()
        else:
            print("Error: missing or additional arguments")
            sys.exit(1)
    
    if args.server:
        if not args.host and args.port and not args.time:
            if not validPort(args.port):
                print("Error: port number must be in the range 1024 to 65535.")
                sys.exit(1)
            server = Server(args.port)
            server.listen()
        else:
            print("Error: missing or additional arguments")
            sys.exit(1)

        