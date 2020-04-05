#!/usr/bin/env python3
# coding=utf-8

import socket
import logger


class CommendSender(object):
    def __init__(self):
        self.host = '127.0.0.1'  # '192.168.2.1' 用于测试
        self.port = 40923
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def __del__(self):
        logger.info("Shuting down socket ...", self)
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()

    def connect(self):
        logger.info("Connecting to %s:%s ..." % (self.host, self.port), self)
        self.socket.connect((self.host, self.port))
        logger.info("Control_commend port connected.", self)

        for i in range(3):
            recv = self.send("command")
            if recv == 'OK':
                logger.info("Entered commend mode successfully.", self)
                break
            else:
                logger.warn(
                    "Unable to enter commend mode. Recevied: %s. Retrying %d ..." % (recv, i), self)

    def send(self, cmd):
        try:
            self.socket.send(cmd.encode('utf-8'))
            recv = self.socket.recv(1024)
            return recv.decode('utf-8')
        except socket.error as e:
            logger.warn(
                "An error occured at sending '%s': %s" % (cmd, e), self)


if __name__ == "__main__":
    sender = CommendSender()
    while True:
        cmd = input(">>> please input SDK cmd: ")
        sender.send(cmd)

        if cmd.upper() == 'Q':
            break
