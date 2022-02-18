#!/usr/bin/env python3

import argparse
import socket

def receive(sock):
	"""Receive a message from the socket
	
	Returns a string, which is expected to be HTTP response.
	"""
	response_msg = b''
	while True:
		buf = sock.recv(1024)
		if not buf:
			break
		response_msg += buf
	return response_msg.decode()

# add --url --user --password --localfile arguments
parser = argparse.ArgumentParser(description='Upload an image file to wordpress media library. ')
parser.add_argument('--url')
parser.add_argument('--user')
parser.add_argument('--password')
parser.add_argument('--localfile')
args = parser.parse_args()
url = args.url
user = args.user
password = args.password
localfile = args.localfile

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
response_msg = receive(sock)

# <div id="login_error"> in response_msg => failed
if 'login_error' in response_msg:
    print('Upload failed.')
    exit()

# login success. get cookie
cookie = ''
for s in response_msg.split('\r\n'):
	if 'Set-Cookie:' in s:
		cookie += ' '+s.split(' ')[1]

# send GET request with cookie to get ___wpnonce value
request_msg  = 'GET /wp-admin/media-new.php HTTP/1.1\r\n'
request_msg += 'Host: ' + url + '\r\n'
request_msg += 'Cookie:' + cookie + '\r\n'
request_msg += 'Connection: close\r\n'
request_msg += '\r\n\r\n'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
sock.sendall(request_msg.encode())

response_msg = receive(sock)

pos = response_msg.find('"_wpnonce":"')
wpnonce = response_msg[pos+12:pos+22]

# upload image using POST request
with open(localfile, "rb") as image:
	f = image.read()
filename =localfile.split('/')[-1].encode()
fileext = localfile.split('.')[-1].encode()

request_body  = b'\r\n------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="name"\r\n\r\n' + filename + b'\r\n'
request_body += b'------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="post_id"\r\n\r\n0\r\n------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="_wpnonce"\r\n\r\n' + wpnonce.encode() + b'\r\n'
request_body += b'------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="type"\r\n\r\n\r\n------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="tab"\r\n\r\n\r\n------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="short"\r\n\r\n1\r\n------WebKitFormBoundary6ooE22qahELw1wPX\r\nContent-Disposition: form-data; name="async-upload"; filename="' + filename + b'"\r\nContent-Type: image/' + fileext + b'\r\n\r\n'
request_body += f
request_body += b'\r\n------WebKitFormBoundary6ooE22qahELw1wPX--\r\n'

request_msg  = 'POST /wp-admin/async-upload.php HTTP/1.1\r\n'
request_msg += 'Host: ' + url + '\r\n'
request_msg += 'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary6ooE22qahELw1wPX\r\n'
request_msg += 'Content-Length: ' + str(len(request_body)) + '\r\n'
request_msg += 'Cookie:' + cookie + '\r\n'
request_msg += 'Connection: close\r\n'
request_msg  = request_msg.encode() + request_body

# "upload file" request
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
sock.sendall(request_msg)
response_msg = receive(sock)

# get attachment_id in "upload file" response body
attachment_id = response_msg.split('\r\n')[-1]

# post attachment_id to get File upload url
request_body = 'attachment_id=' + attachment_id + '&fetch=3'
request_msg  = 'POST /wp-admin/async-upload.php HTTP/1.1\r\n'
request_msg += 'Host: ' + url + '\r\n'
request_msg += 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8\r\n'
request_msg += 'Content-Length: ' + str(len(request_body)) + '\r\n'
request_msg += 'Cookie:' + cookie + '\r\n'
request_msg += 'Connection: close\r\n\r\n'
request_msg += request_body

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
sock.sendall(request_msg.encode())
response_msg = receive(sock)

if 'data-clipboard-text=' in response_msg:
	print('Upload success. File upload url: ', end='')
	start = response_msg.find('data-clipboard-text="')
	end = response_msg.find('">Copy URL to clipboard')
	print(response_msg[start+21:end])
else:
	print('Upload failed.')

sock.close()