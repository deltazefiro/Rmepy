#!/usr/bin/env python3
# coding=utf-8

from commend_sender import  CommendSender
from  attr_push_receiver import  AttrPushReceiver
from logger import Logger

class RMEP(object):
    def __init__(self):
        self.cmd_sender = CommendSender(host='127.0.0.1')
        self.send = self.cmd_sender.send
        self.send_cmd = self.cmd_sender.send_commend
        self.send_query = self.cmd_sender.send_query
        self.logger = Logger('RMEP(main)')

if __name__ == "__main__":
    r = RMEP()
    while True:
        cmd = input(">>> please input SDK cmd: ")
        r.send_query(cmd)

        if cmd.upper() == 'Q':
            break