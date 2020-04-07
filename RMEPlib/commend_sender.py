#!/usr/bin/env python3
# coding=utf-8

import socket
import time
from . import  logger


class CommendSender(object):
    def __init__(self, host='192.168.2.1', port=40923, retry_interval=1):
        self.host = host
        self.port = port
        self.retry_interval = retry_interval
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log = logger.Logger(self)
        # self.connect()

    def __del__(self):
        self.log.info("Shuting down CommendSender ...")
        # self.socket.shutdown()
        self.socket.close()

    def connect(self, retry=3):
        self.log.info("Connecting to %s:%s ..." % (self.host, self.port))

        try:
            self.socket.connect((self.host, self.port))
            self.log.info("ControlCommend port connected.")
        except socket.error as e:
            self.log.warn("Fail to connect to S1. Error: %s" % e)
            if retry > 0:
                time.sleep(self.retry_interval)
                self.log.warn("Retrying...")
                self.connect(retry-1)
            else:
                self.log.error("Failed to retry.")
                self.connect(3)

        # for i in range(3):
        #     recv = self.send("command")
        #     if recv == 'OK':
        #         logger.info("Entered commend mode successfully.", self)
        #         break
        #     else:
        #         time.sleep(self.retry_interval)
        #         logger.warn(
        #             "Unable to enter commend mode. Recevied: %s. Retrying %d ..." % (recv, i), self)

    def send(self, cmd):
        """ Send a commend to S1.

        Args:
            cmd: (str) 命令

        Returns:
            error_code: (int) 错误码
                (0: 无错误，1: 发送时出错，2: 接收回应时出错)
        """
        try:
            self.socket.send(cmd.encode('utf-8'))
        except socket.error as e:
            return 1, e

        try:
            recv = self.socket.recv(1024)
            return 0, recv.decode('utf-8')
        except socket.error as e:
            return 2, e

    def send_commend(self, cmd, n_retries=3):
        error, response = self.send(cmd)
        if error == 1:
            self.log.warn("Error at sending '%s': %s" % (cmd, response))
        if error == 2:
            self.log.error(
                "Error at receiving the response of '%s': %s" % (cmd, response))
        elif response == 'OK':
            self.log.info("'%s' recevied 'OK'." % cmd)
            return
        else:
            self.log.warn(
                "Received an error when executing '%s ': %s" % (cmd, response))

        if n_retries > 0:
            time.sleep(self.retry_interval)
            self.log.warn("Retrying...")
            self.send_commend(cmd, n_retries-1)
        else:
            self.log.error("Failed to retry.")
            self.send_commend(cmd, 3)

    def send_query(self, cmd, n_retries=3):
        error, response = self.send(cmd)
        if error == 1:
            self.log.warn("Error at sending '%s': %s" % (cmd, response))
        if error == 2:
            self.log.error(
                "Error at recevied the response of '%s': %s" % (cmd, response))
        elif response == '':
            self.log.warn("Got null response of '%s'." %cmd)
        else:
            self.log.info("'%s' received '%s'." %(cmd, response))
            return response

        if n_retries > 0:
            time.sleep(self.retry_interval)
            self.log.warn("Retrying...")
            self.send_commend(cmd, n_retries-1)
        else:
            self.log.error("Failed to retry.")
            self.send_commend(cmd, 3)


if __name__ == "__main__":
    sender = CommendSender(host='127.0.0.1')
    while True:
        cmd = input(">>> please input SDK cmd: ")
        sender.send_query(cmd)

        if cmd.upper() == 'Q':
            break
