#!/usr/bin/env python3
# coding=utf-8

import queue

from . import robot_modules
from .logger import Logger
from .robot_connection import CommendSender
from .robot_msg_push import RobotMsgPush
from .robot_video_stream import RobotVideoStream


class Robot(object):
    def __init__(self, ip='192.168.2.1'):
        self.ip = ip

        self.CommendSender = CommendSender(self)
        self.send = self.CommendSender.send
        self.send_cmd = self.CommendSender.send_commend
        self.send_query = self.CommendSender.send_query
        self.connect = self.CommendSender.connect

        # modules (NOTE robot_modules必须在push前申明)
        self.basic_ctrl = robot_modules.BasicCtrl(self)
        self.chassis = robot_modules.Chassis(self)
        self.gimbal = robot_modules.Gimbal(self)
        self.blaster = robot_modules.Blaster(self)

        self.video = RobotVideoStream(self)
        self.push = RobotMsgPush(self)

        self.log = Logger('RMEP(main)')
