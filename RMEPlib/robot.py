#!/usr/bin/env python3
# coding=utf-8

import queue

from .commend_sender import CommendSender
from .push_data_receiver import PushDataReceiver
from .video_stream_receiver import VideoStreamReceiver
from . import commends
from .logger import Logger


class Robot(object):
    def __init__(self):
        self.ip = '127.0.0.1'

        self.CommendSender = CommendSender(self)
        self.send = self.CommendSender.send
        self.send_cmd = self.CommendSender.send_commend
        self.send_query = self.CommendSender.send_query
        self.connect = self.CommendSender.connect

        self.VideoStreamReceiver = VideoStreamReceiver(self)
        self.video_buffer = queue.deque(maxlen=64)

        self.PushDataReceiver = PushDataReceiver(self)
        self.push_buffer = queue.deque(maxlen=10)

        self.basic_ctrl = commends.BasicCtrl(self)
        self.logger = Logger('RMEP(main)')
