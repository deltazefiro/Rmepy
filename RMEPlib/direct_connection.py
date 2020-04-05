#!/usr/bin/env python3
# coding=utf-8

import socket
import warnings
s = socket.socket()

class CommendSender(object):
    def __init__(self):
        self.host = '127.0.0.1'  # '192.168.2.1'
        self.port = 40923
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def __del__(self):
        print("Shuting down socket ...")
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
    
    def connect(self):
        print("Connecting to %s:%s ..." %(self.host, self.port))
        self.socket.connect((self.host, self.port))
        print("Control_commend port connected.")
        recv = self.send("command")
        if recv != 'OK':
            raise Exception("Unable to connect Robomaster S1.")

    def send(self, cmd):
        self.socket.send(cmd.encode('utf-8'))
        try:
                recv = self.socket.recv(1024)
                return recv.decode('utf-8')
        except socket.error as e:
                warnings.warn("An error occured at receving: ", e)
                return None

if __name__ == "__main__":
    sender = CommendSender()
    # sender.connect()
    while True:
        cmd = input(">>> please input SDK cmd: ")
        sender.send(cmd)

        if cmd.upper() == 'Q':
            break

