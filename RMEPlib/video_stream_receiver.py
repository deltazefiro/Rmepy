
"""

VideoStreamRecevier 中的代码 和 libh264decoder 来自 dji-sdk/RoboMaster-SDK
详见 https://github.com/dji-sdk/RoboMaster-SDK/tree/master/sample_code/RoboMasterEP/stream

"""

import queue
import threading
import time
import socket

import cv2
import numpy as np

from . import libh264decoder
from . import logger

class VideoStreamReceiver(object):
    def __init__(self, robot, port='40921'):
        self.robot = robot
        self.ip = robot.ip
        self.port = self.port
        self.log = logger.Logger(self)
        self.running = False


    def bind(self, retry=3):
        self.log.info("Binding to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.bind((self.ip, self.port))
            self.log.info("VideoStream port bound.")
        except socket.error as e:
            self.log.warn("Fail to bind VideoStream port. Error: %s" % e)
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
        pass