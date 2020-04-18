#!/usr/bin/env python3
# coding=utf-8

import queue

from . import commends
from .connection import CommendSender, PushDataReceiver, VideoStreamReceiver
from .logger import Logger
from .robot_video_stream import RobotVideoStream


class Robot(object):
    def __init__(self, ip='192.168.2.1'):
        self.ip = ip

        self.CommendSender = CommendSender(self)
        self.send = self.CommendSender.send
        self.send_cmd = self.CommendSender.send_commend
        self.send_query = self.CommendSender.send_query
        self.connect = self.CommendSender.connect

        self.video = RobotVideoStream(self)

        self.PushDataReceiver = PushDataReceiver(self)
        self.push_buffer = queue.deque(maxlen=10)

        self.basic_ctrl = commends.BasicCtrl(self)
        self.chassis = commends.Chassis(self)
        self.gimbal = commends.Gimbal(self)
        self.log = Logger('RMEP(main)')
