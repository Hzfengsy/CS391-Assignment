from __future__ import print_function
from socket import *
from env import *
import base64
msg = "\r\n I love computer networks!"
endmsg = "\r\n.\r\n"
# Choose a mail server (e.g. Google mail server) and call it mailserver

def sendRecvMsg(msg, return_code):
    if msg:
        clientSocket.send(msg)
    if return_code:
        recv1 = clientSocket.recv(1024)
        print(recv1, end='')
        if recv1[:3] != str(return_code):
            print('%d reply not received from server.' % (return_code))

# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)
sendRecvMsg(None, 220)

# Send HELO command and print server response.
sendRecvMsg('HELO Alice\r\n', 250)

# Send AUTH LOGIN command and print server response.
sendRecvMsg('auth login\r\n', 334)

# Send USER command and print server response.
sendRecvMsg('%s\r\n' %(base64.b64encode(username)), 334)

# Send USER command and print server response.
sendRecvMsg('%s\r\n' %(base64.b64encode(password)), 235)

# Send MAIL FROM command and print server response.
sendRecvMsg('MAIL FROM: %s\r\n' % (mail_from), 250)

# Send RCPT TO command and print server response.
sendRecvMsg('RCPT TO: %s\r\n' % (rcpt_to), 250)

# Send DATA command and print server response.
sendRecvMsg('DATA\r\n', 250)

# Send message data.
sendRecvMsg(msg, None)

# Message ends with a single period.
sendRecvMsg(endmsg, 250)

# Send QUIT command and get server response.
sendRecvMsg('QUIT\r\n', 250)