from __future__ import print_function
from socket import *
from env import *
import base64
msg = "\r\n I love computer networks!\r\n"
endmsg = "\r\n.\r\n"
header = "From: "'Hzfengsy'" <%s>\r\nTo: "'Hzfengsy'"<%s>\r\nSubject: Network Assignment Test\r\n"
boundary = "XX-Hzfengsy-Mail-Client-XX"
MIME_header = "MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary=\"%s\"\r\n" % (boundary)
# Choose a mail server (e.g. Google mail server) and call it mailserver

def sendText(msg):
    text_header = '\r\n'.join(['\r\n',
                               '--%s' % (boundary),
                               'Content-Type: text/plain; charset=us-ascii',
                               '\r\n'])
    sendRecvMsg(text_header)
    sendRecvMsg(msg)

def sendImg(img):
    filename = img.split('/')[-1]
    img_header = '\r\n'.join(['\r\n',
                               '--%s' % (boundary),
                               'Content-Type: image/jpeg; name=%s' % (filename),
                               'Content-Transfer-Encoding: base64',
                               '\r\n'])
    sendRecvMsg(img_header)
    with open(img, 'rb') as f:
        img_data = base64.b64encode(f.read())
        sendRecvMsg(img_data)
    

def sendRecvMsg(msg, return_code=None):
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
sendRecvMsg('DATA\r\n', 354)

# Send header command.
sendRecvMsg(header)
sendRecvMsg(MIME_header)

# Send message data.
sendText(msg)
sendImg("img.jpg")

# Message ends with a single period.
end_MIME = '\r\n\r\n--%s--\r\n' % (boundary)
sendRecvMsg(end_MIME)
sendRecvMsg(endmsg, 250)

# Send QUIT command and get server response.
sendRecvMsg('QUIT\r\n', 221)