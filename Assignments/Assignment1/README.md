# Assignment #1
## 1 - Web Server
This project is a simple web server that handles HTTP requests. Once the web server accept a HTTP ```GET``` request, it creates an HTTP response message with the data of the requested file in correct format. If the requested file is not found, the server will respond an HTTP ```404 Not Found``` message.  

Is pass tests on ```Google Chrome```. But I think it will work well on any other browser.

### Optional Exercises
1. **DONE.** In order to handle several HTTP requests at the same time, the server will create a thread when accepting a new request. I think it is easy to implement.

2. **DONE.** It is easy to write a HTTP client in python too. The client will only send request header ```GET <filename> HTTP/1.1``` to simulation a request from browser.

## 2 - UDP Pinger
In this lab, I write a simple UDP pinger client. The client will send a datagram packets to the server. Once received the response from the server, the client calculate the round trip time (RTT). If no reply is received within some time (one second in this project), the client assume that the packet was lost during transmission across the network.

Every second, the client create a new thread to send a packet. No matter how long the RTT is, the time interval between two sending is exactly one second.

### Optional Exercises
1. **DONE.** Some extra memory and calculate are require in this exercises, which is not difficult.

2. **DONE.** There are two threads running on the server. The main thread check whether the heartbeat packets have been missing for some specified period of time while the other thread receive the packet from client.

## 3 - Mail Client
It is a simple mail sending client using SMTP to send email to mail server. For now every mail server require an authentication before sending a email, it is necessary to add ```auth login``` command into original SMTP message.

### Optional Exercises
1. **DONE.** Send ```STARTTLS``` command after ```HELO``` to connect server in TLS socket. Then send message in the same way as original SMTP but in TLS socket. The client have passed the test on Gmail.

2. **DONE** SMTP is a text-based protocol, that is original SMTP could only send text mail without any picture, video etc. So, it is necessary to use a extension protocol called Multipurpose Internet Mail Extensions (MIME). It costs me some time to learn MIME protocol and write the message in correct format.

## 4 - Proxy Server
The lab requires us to write a simple proxy to request one web page. I filled blanks of the skeleton code, but I could open none website completely. For now, there are few websites can be loaded by only one HTTP GET request. The connection between browser and server is either persistent or multiple.

Because of this, I try to write a full functional proxy server which support not only persistent connection but also HTTPS request. I will introduce my implementation.

For each reqeust, the proxy will create a new thread to handle it. Transmit data is the most important thing a proxy does. In HTTP connection, send all data from browser to remote server and also forward all data from server to browser. Besause the connection bewteen browser and client may be persistent, the connection pass through the proxy server must be persistent too. We don't need to know where a response finish, just transmit all data to the other side. In HTTPS connection, a ```CONNECT``` request will send to proxy in plain text first to ask proxy to connect to remote server. After connection established, the proxy response a message 
```
HTTP/1.1 200 Connection Established
``` 
Then the browser will talk to the remote server in cipher text, and the proxy will only transmit the data just like what it does in HTTP.

Because of unknowing of the end of response, especially in encrypted connection, we cannot determine to receive from remote server or browser at a moment. We have to listen both side all time. Generally, there need two thread in one connection to transmit data. But I use ```epoll```, a Linux kernel system call, for a scalable I/O event notification mechanism.

Since then, our proxy server is fully operational. The only thing remains to do is caching. Ofcourse, the proxy cannot cache any data from HTTPS connection, for we do not know what the browser and server are talking. And in HTTP connection, the proxy could only cache the response of GET request.

Now, it is necessary to know where is the end of a response for GET request. According to the protocol, a client will only send request after recieve all response data in one socket connection. OK, once proxy recieve a new request from browser, the cache file is finished.

That is my implementation of proxy server.

### Optional Exercises
1. **PERHAPS DONE** For now, every HTTP server software, like Apache, Nginx and etc, does return a 404 website. The proxy server will forward this message to the browser.

2. **DONE** Any request which is not in method GET will be forward to remote server directly. 

3. **DONE** For every request in method GET, will hash all message by MD5 algorithm. If there is a cahce file hit this hash code, just respond the browser the data in this file.