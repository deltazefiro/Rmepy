#!/usr/bin/env python3
# coding=utf-8

import socket
import random
from rmepy import logger

HOST = '127.0.0.1'
PORT = 40923

msg = ['OK', 'OK', 'OK', '12dafd 1234', '12 1324 1223', 'OK', '123421 123 11 11']

log = logger.Logger('Tester')


# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.bind((HOST, PORT))
#     s.listen()
#     while True:
#         log.info('Wait for msg ...')
#         conn, addr = s.accept()
#         with conn:
#             log.info('Connected by ' + str(addr))
#             while True:
#                 data = conn.recv(4096).decode('utf-8')
#                 if not data:
#                     log.warn("Server closed.")
#                     break
#                 log.info("Recevied msg: "+ data)
#                 conn.send(random.choice(msg).encode('utf-8'))

data = ('gimbal push attitude 20 10', 'chassis push attitude 0.1 1 3')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    # 发送数据:
    input('Enter ...')
    s.sendto(random.choice(data).encode('utf-8'), ('127.0.0.1', 40924))