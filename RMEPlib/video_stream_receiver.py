
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
from .decorators import  retry

class VideoStreamReceiver(object):
    def __init__(self, robot, port='40921'):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.log = logger.Logger(self)
        self.running = False

    @retry(n_retries=3)
    def bind(self):
        self.log.info("Binding to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.bind((self.ip, self.port))
            self.log.info("VideoStream port bound.")
        except socket.error as e:
            self.log.error("Fail to bind VideoStream port. Error: %s" % e)
            return 


    def start(self):
        self.bind()
        self.running = True
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        self.log.info('VideoStream thread started.')

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.video_decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, int(ls / 3), 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def update(self):
        package_data = b''

        self.connection.start_video_recv()

        while not self.is_shutdown: 
            buff = self.connection.recv_video_data()
            if buff:
                package_data += buff
                if len(buff) != 1460:
                    for frame in self._h264_decode(package_data):
                        try:
                            self.video_decoder_msg_queue.put(frame, timeout=2)
                        except Exception as e:
                            if self.is_shutdown:
                                break
                            print('video decoder queue full')
                            continue
                    package_data=b''

        self.connection.stop_video_recv()
