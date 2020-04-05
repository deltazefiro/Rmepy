#!/usr/bin/env python3
# coding=utf-8

import socket
import time
import logger


class CommendSender(object):
    def __init__(self, host='192.168.2.1', port=40923, retry_interval=1):
        self.host = host  # 用于测试
        self.port = port
        self.retry_interval = retry_interval
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def __del__(self):
        logger.info("Shuting down socket ...", self)
        # self.socket.shutdown()
        self.socket.close()

    def connect(self, retry=3):
        logger.info("Connecting to %s:%s ..." % (self.host, self.port), self)

        try:
            self.socket.connect((self.host, self.port))
            logger.info("Control_commend port connected.", self)
        except socket.error as e:
            logger.warn("Fail to connect to S1. Error: %s" %e, self)
            if retry > 0:
                time.sleep(self.retry_interval)
                logger.warn("Retrying...", self)
                self.connect(retry-1)
            else:
                logger.error("Failed to retry", self)
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
            logger.warn("Error at sending '%s': %s" %(cmd, response), self)
        if error == 2:
            logger.error("Error at receving the response of '%s': %s" %(cmd, response), self)
        elif response == 'OK':
            logger.info("'%s' recevied 'OK'" %cmd)
            return True
        else:
            logger.warn("Recieved an error when executing '%s ': %s" %(cmd, response), self)

        if n_retries > 0:
            time.sleep(self.retry_interval)
            logger.warn("Retrying...", self)
            self.send_commend(cmd, n_retries-1)
        else:
            logger.error("Failed to retry", self)
            self.send_commend(cmd, 3)


if __name__ == "__main__":
    sender = CommendSender(host='127.0.0.1')
    while True:
        cmd = input(">>> please input SDK cmd: ")
        sender.send_commend(cmd)

        if cmd.upper() == 'Q':
            break
