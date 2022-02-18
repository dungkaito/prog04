#!/usr/bin/env python3

import argparse
import socket

# add --url --user --password arguments
parser = argparse.ArgumentParser(description='Login to wordpress admin page.')
parser.add_argument('--url')
parser.add_argument('--user')
parser.add_argument('--password')
args = parser.parse_args()
url = args.url
user = args.user
password = args.password

# get only hostname from url
url = url.replace('http://', '')
url = url.replace('https://', '')
if url[-1] == '/': url = url[:-1]

# connect to server and send POST request to /wp-login.php
request_body = 'log=' + user + '&pwd=' + password
server_address = (url, 80)
request_msg  = 'POST /wp-login.php HTTP/1.1\r\n'
request_msg += 'Host: ' + url + '\r\n'
request_msg += 'Content-Type: application/x-www-form-urlencoded\r\n'
request_msg += 'Content-Length: ' + str(len(request_body)) + '\r\n'
request_msg += 'Connection: close\r\n'
request_msg += '\r\n'
request_msg += request_body
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
sock.sendall(request_msg.encode())

# get response message
response_msg = b''
while True:
    buf = sock.recv(1024)
    if not buf:
        break
    response_msg += buf
sock.close()

# <div id="login_error"> in response_msg => failed
if b'login_error' in response_msg:
    print('User ' + user + ' đăng nhập thất bại')
else:
    print('User ' + user + ' đăng nhập thành công')