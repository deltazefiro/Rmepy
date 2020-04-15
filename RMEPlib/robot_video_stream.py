
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
from . import connection
from .decorators import retry


class RobotVideoStream(object):
    def __init__(self, robot, port=40921, recv_buffer_size=32, display_buffer_size=5,
                 socket_retry_interval=3, socket_time_out=3):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.log = logger.Logger(self)
        self.running = False

        self.video_stream_receiver = connection.VideoStreamReceiver(
            robot, port=port, retry_interval=socket_retry_interval, time_out=socket_time_out, recv_buffer_size=recv_buffer_size)
        self.recv_buffer = self.video_stream_receiver.recv_buffer

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()
        self.display_buffer = queue.deque(maxlen=display_buffer_size)
        self._decoder_thread = threading.Thread(
            target=self._decoder_thread_task)

    def __del__(self):
        self.log.info("Shuting down VideoDecoder thread ...")
        if self.running:
            self._decoder_thread.join()
            self.log.info("Shutted down VideoDecoder thread successfully.")
            self.running = False
        else:
            self.log.info("VideoDecoder thread has not been started. Skip ...")

    def start(self):
        self.running = True
        self.video_stream_receiver.start()

        self._decoder_thread.start()
        self.log.info("VideoStream thread started.")

    def _decoder_thread_task(self):
        package_data = b''

        while self.running:
            try:
                buff = self.decoder_buffer.pop()
            except IndexError:
                self.log.warn("decoder_buffer empty.")
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
                frame = np.fromstring(
                    frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, int(ls / 3), 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list
