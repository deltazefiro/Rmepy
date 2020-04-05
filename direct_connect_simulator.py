#!/usr/bin/env python3
# coding=utf-8

import socket

HOST = '127.0.0.1'  # 标准的回环地址 (localhost)
PORT = 40923        # 监听的端口 (非系统级的端口: 大于 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                print("Server closed. Exiting ...")
                break
            print("Recevied msg:", data)
            conn.send("OK".encode('utf-8'))
