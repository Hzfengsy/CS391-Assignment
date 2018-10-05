import socket 
import time
import numpy as np
import threading
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

addr = ('localhost', 8080)
rtts = []
loss = 0
total = 10
sleep_time = 1.0
UDP_timeout = 1.0
threads = []

def sendUDP(i):
    global loss, rtts
    try:
        start_time = time.time()
        sequence_number = str(i + 1)
        # localtime = time.asctime( time.localtime(start_time) )
        localtime = str(start_time)
        message = ' '.join(['PING', sequence_number, localtime])
        clientSocket.sendto(message.encode(), addr)
        clientSocket.settimeout(UDP_timeout)
        recv_message, address = clientSocket.recvfrom(1024)
        recv_message = recv_message.decode()
        end_time = time.time()
        rtt = (end_time - start_time) * 1000
        rtts.append(rtt)
        print("PING %s: time=%.3f ms" % (sequence_number, rtt))
        print('-->message:' + recv_message)
    except socket.timeout:
        loss += 1
        print("PING %s: Request timed out." % sequence_number)
try:
    for i in range(total):
        thread = threading.Thread(target=sendUDP, args=(i,))
        thread.start()
        threads.append(thread)
        time.sleep(sleep_time)

except KeyboardInterrupt:
    pass

finally:
    for thread in threads:
        thread.join()
    print("%d packets transmitted, %d packets received, %.1f%% packet loss" % (total, total - loss, loss / total * 100))
    if len(rtts) > 0:
        print("round-trip time min/avg/max = %.3f/%.3f/%.3f ms" % (min(rtts), np.mean(rtts), max(rtts)))
    clientSocket.close()