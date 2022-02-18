#!/usr/bin/env python3

import argparse
import socket

# add --url --remotefile arguments
parser = argparse.ArgumentParser(description='Download an image from wordpress page.')
parser.add_argument('--url')
parser.add_argument('--remotefile')
args = parser.parse_args()
url = args.url
remotefile = args.remotefile

# get only hostname from url
url = url.replace('http://', '')
url = url.replace('https://', '')
if url[-1] == '/': url = url[:-1]

# connect to server and send GET request to remotefile
server_address = (url, 80)
request_msg  = b'GET ' + remotefile.encode() + b' HTTP/1.1\r\n'
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

if b'Content-Type: image/' not in response_msg:
	print('Không tồn tại file ảnh')
	exit()

# remove header, get body (image in bytes)
img_bytes = response_msg.decode('iso-8859-1').split('\r\n\r\n')[1].encode('iso-8859-1')
print('Kích thước file ảnh: ' + str(len(img_bytes)) + ' bytes') 
with open(remotefile.split('/')[-1], 'wb') as handler:
    handler.write(img_bytes)