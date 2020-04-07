#!/usr/bin/env python3
# coding=utf-8

from .commend_sender import CommendSender
from .attr_push_receiver import AttrPushReceiver
from .logger import Logger

class Robot(object):
    def __init__(self):
        self.CommendSender = CommendSender(host='127.0.0.1')
        self.connect = self.CommendSender.connect
        self.send = self.CommendSender.send
        self.send_cmd = self.CommendSender.send_commend
        self.send_query = self.CommendSender.send_query
        self.logger = Logger('RMEP(main)')

if __name__ == "__main__":
    r = Robot()
    r.connect()
    while True:
        cmd = input(">>> please input SDK cmd: ")
        r.send_query(cmd)

        if cmd.upper() == 'Q':
            break