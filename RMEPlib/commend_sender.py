#!/usr/bin/env python3
# coding=utf-8

import socket
from . import logger
from .decorators import retry


class CommendSender(object):
    """用于向s1发送控制命令

    Attributes:
        robot: robot对象
        port: 控制命令端口40923
        retry_interval: 发送失败重试的间隔时间

    """

    def __init__(self, robot, port=40923, retry_interval=1, time_out=3):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.retry_interval = retry_interval
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(time_out)
        self.log = logger.Logger(self)

        # robot.send = self.send
        # robot.send_cmd = self.send_commend
        # robot.send_query = self.send_query
        # robot.connect = self.connect
        # self.connect()

    def __del__(self):
        self.log.info("Shuting down CommendSender ...")
        # self.socket.shutdown()
        self.socket.close()

    @retry(n_retries=1e8)
    def connect(self):
        """Connect to s1.

        连接robomaster s1

        Args:
            None

        Returns:
            error: (int) 错误码
            None: (None) 用于适配修饰器

        """
        self.log.info("Connecting to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.connect((self.ip, self.port))
            self.log.info("ControlCommend port connected.")
            return True
        except socket.error as e:
            self.log.warn("Fail to connect to S1. Error: %s" % e)
            return False

    def send(self, cmd):
        """ Send a commend to S1.

        Args:
            cmd: (str) 命令

        Returns:
            (tuple) (
                succ (bool): 是否成功
                response (str): 来着机器人的回复
            )

        """
        try:
            self.socket.sendall(cmd.encode('utf-8'))
        except socket.error as e:
            self.log.warn("Error at sending '%s': %s" % (cmd, e))
            return False, None
        try:
            recv = self.socket.recv(4096)
        except socket.error as e:
            self.log.error(
                "Error at receving the response of '%s': %s" % (cmd, e))
            return False, None
        return True, recv.decode('utf-8')

    @retry(n_retries=3)
    def send_commend(self, cmd):
        """Send a commend which does not require returns.

        向s1发送一个不需要返回值的命令
        即若执行成功s1只返回'OK'的命令，如 'connect' 命令

        Args:
            cmd: (str) 命令

        Returns:
            (succ: (bool) 是否成功，被修饰器使用)
            None
        """
        succ, response = self.send(cmd)
        if succ:
            if response == 'OK':
                self.log.info("'%s' recevied 'OK'." % cmd)
                return True
            elif response == '':
                self.log.warn("Got null response of '%s'." % cmd)
            else:
                self.log.warn(
                    "Received an error when executing '%s': %s" % (cmd, response))
        return False

    @retry(n_retries=3)
    def send_query(self, cmd):
        """Send a commend which requires returns.

        向s1发送一个询问性的（需要返回值的）命令
        即所以以'?'结尾的命令，如 'robot mode ?' 命令

        Args:
            cmd: (str) 命令

        Returns:
            (succ: (bool) 是否成功，被修饰器使用)
            response: (str) 来自s1的返回值

        """
        succ, response = self.send(cmd)

        if succ:
            if response == '':
                self.log.warn("Got null response of '%s'." % cmd)
            else:
                self.log.info("'%s' received '%s'." % (cmd, response))
                return True, response

        return False, None
