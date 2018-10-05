# We will need the following module to generate randomized lost packets
import random
import socket
import threading
import time
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('0.0.0.0', 8080))

clients = {}
lock = threading.Lock()
timeout = 5.0
delay = 1.0 

def recvMsg():
    def messageDecode(message):
        _, index, timeStamp = message.split(' ', 2)
        return int(index), float(timeStamp)

    global clients
    try:
        while True:
            # Generate random number in the range of 0 to 10
            rand = random.randint(0, 10)
            # Receive the client packet along with the address it is coming from
            message, address = serverSocket.recvfrom(1024)
            index, timeStamp = messageDecode(message.decode())
            lock.acquire()
            if address in clients:
                clients[address]['total'] += index - clients[address]['last']
                clients[address]['loss']  += index - clients[address]['last'] - 1
                clients[address]['last']  = index
                clients[address]['time']  = timeStamp
            else:
                print('client %s connected' % (str(address)))
                clients[address] = {'total': 1, 'loss': 0, 'last': index, 'time': timeStamp}
            lock.release()
            # Capitalize the message from the client
            message = message.upper()
            # If rand is less is than 4, we consider the packet lost and do not respond
            if rand < 4:
                continue
            # Otherwise, the server responds
            serverSocket.sendto(message, address)
    except: 
        pass

thread = threading.Thread(target=recvMsg)
thread.start()
try:
    while True:
        lock.acquire()
        for client in list(clients.keys()):
            info = clients[client]
            if time.time() - info['time'] > timeout:
                total, loss = info['total'], info['loss']
                print('client %s heartbeat timeout' % (str(client)))
                print("%d packets transmitted, %d packets received, %.1f%% packet loss" % (total, total - loss, loss / total * 100))
                clients.pop(client)
        lock.release()
        time.sleep(delay)
except KeyboardInterrupt:
    pass
finally:
    serverSocket.close()



