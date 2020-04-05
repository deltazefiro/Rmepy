#!/usr/bin/env python3
# coding=utf-8

import socket
import logger

HOST = '127.0.0.1'  # 标准的回环地址 (localhost)
PORT = 40923        # 监听的端口 (非系统级的端口: 大于 1023)

msg = ['OKadf', 'adsfadsf', 'OK']

i = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    logger.info('Wait for msg ...', 'tester')
    conn, addr = s.accept()
    with conn:
        logger.info('Connected by ' + str(addr), 'tester')
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                logger.info("Server closed. Exiting ...", 'tester')
                break
            logger.info("Recevied msg: "+ data, 'tester')
            conn.send(msg[i].encode('utf-8'))
            i += 1
