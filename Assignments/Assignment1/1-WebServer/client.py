import socket
import sys

def request(ip, port, filename):
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((ip, port))

    message = "GET /" + filename + " HTTP/1.1\r\n\r\n"
    clientSocket.send(message.encode())

    data = clientSocket.recv(1024)
    clientSocket.close()
    return data.decode()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Format Error. Please use the proper format:")
        print("    client.py server_host server_port filename")
        sys.exit()
    print(request(sys.argv[1], int(sys.argv[2]), sys.argv[3]))

