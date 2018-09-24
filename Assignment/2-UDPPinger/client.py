from socket import *
import time
import numpy as np
clientSocket = socket(AF_INET, SOCK_DGRAM)

addr = ('localhost', 8080)
rtts = []
loss = 0.0
total = 10
for i in range(total):
    try:
        start_time = time.time()
        sequence_number = str(i + 1)
        localtime = time.asctime( time.localtime(start_time) )
        message = ' '.join(['PING', sequence_number, localtime])
        clientSocket.sendto(message, addr)
        clientSocket.settimeout(1.0)
        recv_message, address = clientSocket.recvfrom(1024)
        end_time = time.time()
        rtt = (end_time - start_time) * 1000
        rtts.append(rtt)
        print("PING %s: time=%.3f ms" % (sequence_number, rtt))
        print('-->message:' + recv_message)
    except timeout:
        loss += 1
        print("PING %s: Request timed out." % sequence_number)

print("%d packets transmitted, %d packets received, %.1f%% packet loss" % (total, total - loss, loss / total * 100))
print("round-trip time min/avg/max = %.3f/%.3f/%.3f ms" % (min(rtts), np.mean(rtts), max(rtts)))
clientSocket.close()