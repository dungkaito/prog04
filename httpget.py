#!/usr/bin/env python3

import argparse
import socket

# add --url argument
parser = argparse.ArgumentParser(description='Get the title of html page.')
parser.add_argument('--url')
args = parser.parse_args()
url = args.url

# get only hostname from url
url = url.replace("http://", "")
url = url.replace("https://", "")
if url[-1] == '/': url = url[:-1]

# connect to server and send GET request to /
server_address = (url, 80)
request_msg  = b'GET / HTTP/1.1\r\n'
request_msg += b'Host: ' + url.encode() + b'\r\n'
request_msg += b'Connection: close\r\n'
request_msg += b'\r\n'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
sock.sendall(request_msg)

# get response message
response_msg = b''
while True:
    buf = sock.recv(1024)
    if not buf:
        break
    response_msg += buf
sock.close()

# print value of html `title` tag
response_msg = response_msg.decode()
start = response_msg.find('<title>')
end = response_msg.find('</title>')
from html import unescape
print(unescape(response_msg[start+7:end]))