
"""

RobotVideoStream 中的部分代码 和 libh264decoder 来自 dji-sdk/RoboMaster-SDK
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
from .decorators import retry


class RobotVideoStream(object):
    def __init__(self, robot, port=40921, decoder_buffer_size=32, display_buffer_size=5):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.log = logger.Logger(self)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()

        self.decoder_buffer = queue.deque(maxlen=decoder_buffer_size)
        self.display_buffer = queue.deque(maxlen=display_buffer_size)

        self._receiver_thread = threading.Thread(target=self._receiver_thread_task)
        self._decoder_thread = threading.Thread(target=self._decoder_thread_task)

        self.running = False

    def __del__(self):
        self.log.info("Shuting down VideoStreamReceiver ...")
        if self.running:
            self.running = False
            self._decoder_thread.join()
            self._receiver_thread.join()
            self.log.info("Shutted down VideoStreamReceiver thread successfully.")
            self.socket.close()
        else:
            self.log.info("VideoStreamReceiver thread has not been started. Skip ...")

    def start(self):
        self.robot.basic_ctrl.video_stream_on()
        self._bind()
        self._establish()
        self.running = True

        self._receiver_thread.start()
        self._decoder_thread.start()
        self.log.info("VideoStream thread started.")

    @retry(n_retries=3)
    def _bind(self):
        # self.log.info("Binding to %s:%s ..." % (self.ip, self.port))
        try:
            self.socket.bind((self.ip, self.port))
        except socket.error as e:
            self.log.error("Fail to bind VideoStream port. Error: %s" % e)
            return False
        else:
            self.log.info("VideoStream port bound.")
            return True

    @retry(n_retries=3)
    def _establish(self):
        self.socket.listen()
        try:
            self.conn, _ = self.socket.accept()
        except socket.error as e:
            self.log.error("Fail to establish video stream. Error: %s" % e)
            return False
        else:
            self.log.info("Video stream established.")
            return True

    def _receiver_thread_task(self):
        while self.running:
            try:
                data = self.conn.recv(4096)
                if data:
                    self.decoder_buffer.appendleft(data)
                elif self.running:
                    self.log.error("Got a null msg from the video stream.")
            except socket.timeout:
                if self.running:
                    self.log.warn("Nothing has been received from VideoStream port. (timeout)")

    def _decoder_thread_task(self):
        package_data = b''

        while self.running:
            try:
                buff = self.decoder_buffer.pop()
            except IndexError:
                # self.log.warn("decoder_buffer empty.")
                continue
            else:
                package_data += buff
                if len(buff) != 1460:
                    frames = self._h264_decode(package_data)
                    if frames:
                        self.display_buffer.extendleft(frames)
                    package_data = b''

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
