
"""

RobotVideoStream 中的部分代码 和 libh264decoder 来自 dji-sdk/RoboMaster-SDK
详见 https://github.com/dji-sdk/RoboMaster-SDK/tree/master/sample_code/RoboMasterEP/stream

"""

import queue
import socket
import threading
import time

import cv2
import numpy as np
from PIL import Image as PImage

from . import robot_connection, logger
from .decoders import libh264decoder
from .decorators import retry


class RobotVideoStream(object):
    def __init__(self, robot, port=40921, recv_buffer_size=32, display_buffer_size=5, socket_time_out=3):
        self.robot = robot
        self.log = logger.Logger(self)
        self.running = False
        self.display_running = False

        self.video_stream_receiver = robot_connection.VideoStreamReceiver(
            robot, port=port, time_out=socket_time_out, recv_buffer_size=recv_buffer_size)
        self.recv_buffer = self.video_stream_receiver.recv_buffer

        self.video_decoder = libh264decoder.H264Decoder()
        libh264decoder.disable_logging()
        self.display_buffer = queue.deque(maxlen=display_buffer_size)
        self._decoder_thread = threading.Thread(target=self._decoder_thread_task)
        self._display_thread = threading.Thread(target=self._display_thread_task)

    def __del__(self):
        if self.display_running:
            self.log.debuginfo("Shuting down Display thread ...")
            self.display_running = False
            self._display_thread.join()
            self.log.debuginfo(
                'Shutted down Display thread successfully.')
        else:
            self.log.debuginfo(
                'Display thread has not been started. Skip ...')

        if self.running:
            self.log.debuginfo("Shuting down VideoDecoder thread ...")
            self.running = False
            self._receiver_thread.join()
            self.log.debuginfo(
                'Shutted down VideoDecoder thread successfully.')
        else:
            self.log.debuginfo(
                'VideoDecoder thread has not been started. Skip ...')


    def start(self):
        self.video_stream_receiver.start()
        self._decoder_thread.start()
        self.log.info("VideoStream thread started.")

    def display(self):
        self._display_thread.start()
        self.log.info("Display thread started.")

    def _decoder_thread_task(self):
        self.running = True
        package_data = b''

        while self.running:
            try:
                buff = self.recv_buffer.pop()
            except IndexError:
                self.log.debuginfo("recv_buffer empty.")
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

    def _display_thread_task(self):
        self.display_running = True
        while self.display_running:
            frame = self.get_frame()
            if frame:
                image = PImage.fromarray(frame)
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                cv2.imshow("Liveview", img)
            cv2.waitKey(34) # 30 fps

    def get_last_frame(self):
        try:
            return self.display_buffer[0]
        except IndexError:
            self.log.warn("Fail to get last frame: display buffer empty.")
            return None

    def get_frame(self):
        try:
            return self.display_buffer.pop()
        except IndexError:
            self.log.warn("Fail to get frame: display buffer empty.")

    @property
    def last_frame(self):
        return self.get_last_frame()
