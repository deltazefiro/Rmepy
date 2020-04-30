#!/usr/bin/env python3
# coding=utf-8

import socket
import random
from rmepy import logger
from time import sleep

HOST = '127.0.0.1'
PORT = 40923

msg = ['OK', 'OK', 'OK', '12dafd 1234', '12 1324 1223', 'OK', '123421 123 11 11']

class Test():

    def __del__(self):
        try:
            cmd_s.close()
        except Exception:
            pass

        try:
            eve_s.close()
        except Exception:
            pass

        try:
            video_s.close()
        except Exception:
            pass

    log = logger.Logger('Tester')

    cmd_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmd_s.bind((HOST, 40923))
    cmd_s.listen()

    cmd_conn, _ = cmd_s.accept()
    log.debug('Cmd_s conned')
    
    eve_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    eve_s.bind((HOST, 40925))
    eve_s.listen()

    eve_conn, _ = eve_s.accept()
    log.debug('Eve_s conned')

    # while True:
    #     try:
    #         cmd_conn.recv(4096)
    #         video_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         video_s.connect((HOST, 40921))
    #         break
    #     except Exception as e:
    #         log.info('Waiting for video conn ...: %s' %e)
    #         sleep(1)

    while True:
        log.info('Wait for msg ...')
        with cmd_conn:
            while True:
                data = cmd_conn.recv(4096).decode('utf-8')
                if not data:
                    log.warn("Server closed.")
                    break
                log.info("Recevied msg: "+ data)
                cmd_conn.send(random.choice(msg).encode('utf-8'))

    # data = ('gimbal push attitude 20 10', 'chassis push attitude 0.1 1 3')
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # while True:
    #     # 发送数据:
    #     input('Enter ...')
    #     s.sendto(random.choice(data).encode('utf-8'), ('127.0.0.1', 40924))

if __name__ == "__main__":
    Test()