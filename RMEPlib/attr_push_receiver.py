#!/usr/bin/env python3
# coding=utf-8

import socket
import time
import threading
import queue
from . import logger


class AttrPushReceiver(object):
    def __init__(self, robot, port=40924):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log = logger.Logger(self)
        self.running = False

    def __del__(self):
        self.log.info("Shuting down AttrPushReceiver ...")
        self.running = False
        try:
            self.thread.join()
            self.log.info('Shutted down AttrPushReceiver thread successfully.')
        except AttributeError:
            self.log.warn(
                'AttrPushReceiver thread has not been started. Skip ...')
        self.socket.close()

    def bind(self, retry=3):
        self.log.info("Binding to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.bind((self.ip, self.port))
            self.log.info("AttrPush port bound.")
        except socket.error as e:
            self.log.warn("Fail to bind AttrPush port. Error: %s" % e)
            if retry > 0:
                time.sleep(self.retry_interval)
                self.log.warn("Retrying...")
                self.connect(retry-1)
            else:
                self.log.error("Failed to retry")
                self.bind(3)

    def start(self):
        self.bind()
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        self.log.info('AttrPushReceiver thread started.')

    def update(self):
        self.socket.settimeout(1)
        while self.running:
            try:
                recv = self.socket.recv(1024).decode('utf-8')
                self.robot.attr_buffer.appendleft()
            except socket.timeout:
                continue
            except socket.error as e:
                self.log.warn("Error at decoding: %s" % e)


if __name__ == "__main__":
    test = AttrPushReceiver('127.0.0.1')
    test.start()
    import time
    time.sleep(3)
