#!/usr/bin/env python3
# coding=utf-8

import socket
import time
import logger
import threading

class AttrPushReceiver(object):
    def __init__(self, host='192.168.2.1', port=40924):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log = logger.Logger(self)
    
    def __del__(self):
        self.log.info("Shuting down AttrPushReceiver ...")
        try:
            self.thread.join()
            self.log.info('Shutted down AttrPushReceiver thread successfully.')
        except AttributeError:
            self.log.warn('AttrPushReceiver thread has not be started. Skip ...')
        self.socket.close()
    
    def bind(self, retry=3):
        self.log.info("Binding to %s:%s ..." % (self.host, self.port))

        try:
            self.socket.bind((self.host, self.port))
            self.log.info("AttrPush port bound.")
        except socket.error as e:
            self.log.warn("Fail to bound AttrPush port. Error: %s" % e)
            if retry > 0:
                time.sleep(self.retry_interval)
                self.log.warn("Retrying...")
                self.connect(retry-1)
            else:
                self.log.error("Failed to retry")
                self.bind(3)
    
    def start(self):
        self.bind()
        self.thread = threading.Thread(None, self.update)
        self.thread.start()
        self.log.info('AttrPushReceiver thread started.')

    def update(self):
        pass

if __name__ == "__main__":
    test = AttrPushReceiver('127.0.0.1')
    test.start()
    import time
    time.sleep(10)