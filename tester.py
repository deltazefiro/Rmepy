#!/usr/bin/env python3
# coding=utf-8

import socket
from RMEPlib import logger

HOST = '127.0.0.1'
PORT = 40923

msg = ['OKadf', 'adsfadsf', 'OK']

log = logger.Logger('Tester')
i = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    log.info('Wait for msg ...')
    conn, addr = s.accept()
    with conn:
        log.info('Connected by ' + str(addr))
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                log.info("Server closed. Exiting ...")
                break
            log.info("Recevied msg: "+ data)
            conn.send(msg[i].encode('utf-8'))
            i += 1
