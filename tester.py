#!/usr/bin/env python3
# coding=utf-8

import socket
from RMEPlib import logger

HOST = '127.0.0.1'
PORT = 40923

msg = ['OK', 'OK', 'OK', '12dafd 1234', '12 1324 1223', 'OK']

log = logger.Logger('Tester')

while True:
    try:
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
                        log.warn("Server closed. Exiting ...")
                        break
                    log.info("Recevied msg: "+ data)
                    conn.send(msg[i].encode('utf-8'))
                    i += 1
    except Exception as e:
        log.warn(e)
