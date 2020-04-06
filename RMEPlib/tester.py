#!/usr/bin/env python3
# coding=utf-8

import socket
import logger

HOST = '127.0.0.1'  # 标准的回环地址 (localhost)
PORT = 40923        # 监听的端口 (非系统级的端口: 大于 1023)

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
