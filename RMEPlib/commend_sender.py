#!/usr/bin/env python3
# coding=utf-8

import socket
import time
from . import logger
from functools import wraps


def retry(n_retries):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            retry = 0
            while retry < n_retries:
                error, response = func(*args, **kwargs)
                if not error:
                    return response
                retry += 1
                time.sleep(args[0].retry_interval)
                args[0]._log.warn("Retrying %d ..." % retry)
            args[0]._log.error("Failed to retry.")
            return None

        return wrapper
    return decorator



class CommendSender(object):
    """用于向s1发送控制命令

    Attributes:
        robot: robot对象
        port: 控制命令端口40923
        retry_interval: 发送失败重试的间隔时间

    """

    def __init__(self, robot, port=40923, retry_interval=1):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.retry_interval = retry_interval
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._log = logger.Logger(self)

        # robot.send = self.send
        # robot.send_cmd = self.send_commend
        # robot.send_query = self.send_query
        # robot.connect = self.connect
        # self.connect()

    def __del__(self):
        self._log.info("Shuting down CommendSender ...")
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
        self._log.info("Connecting to %s:%s ..." % (self.ip, self.port))

        try:
            self.socket.connect((self.ip, self.port))
            self._log.info("ControlCommend port connected.")
            error = 0
        except socket.error as e:
            self._log.warn("Fail to connect to S1. Error: %s" % e)
            error = 1

        return error, None

    def send(self, cmd):
        """ Send a commend to S1.

        Args:
            cmd: (str) 命令

        Returns:
            error_code: (int) 错误码
                {0: 无错误，1: 发送时出错，2: 接收回应时出错}

        """
        try:
            self.socket.send(cmd.encode('utf-8'))
        except socket.error as e:
            return 1, e

        try:
            recv = self.socket.recv(1024)
            return 0, recv.decode('utf-8')
        except socket.error as e:
            return 2, e

    @retry(n_retries=3)
    def send_commend(self, cmd):
        """Send a commend which does not require returns.

        向s1发送一个不需要返回值的命令
        即若执行成功s1只返回'OK'的命令，如 'connect' 命令

        Args:
            cmd: (str) 命令

        Returns:
            error: (int) 错误码
            None: (None) 用于适配修饰器

        """
        error, response = self.send(cmd)
        if error == 1:
            self._log.warn("Error at sending '%s': %s" % (cmd, response))
        elif error == 2:
            self._log.error(
                "Error at receiving the response of '%s': %s" % (cmd, response))
        elif response == '':
            error = 3
            self._log.warn("Got null response of '%s'." % cmd)
        elif response == 'OK':
            self._log.info("'%s' recevied 'OK'." % cmd)
        else:
            error = 4
            self._log.warn(
                "Received an error when executing '%s': %s" % (cmd, response))

        return error, None

    @retry(n_retries=3)
    def send_query(self, cmd):
        """Send a commend which requires returns.

        向s1发送一个询问性的（需要返回值的）命令
        即所以以'?'结尾的命令，如 'robot mode ?' 命令

        Args:
            cmd: (str) 命令

        Returns:
            error: (int) 错误码
            response: (str) 来自s1的返回值

        """
        error, response = self.send(cmd)
        if error == 1:
            self._log.warn("Error at sending '%s': %s" % (cmd, response))
        if error == 2:
            self._log.error(
                "Error at recevied the response of '%s': %s" % (cmd, response))
        elif response == '':
            error = 3
            self._log.warn("Got null response of '%s'." % cmd)
        else:
            self._log.info("'%s' received '%s'." % (cmd, response))

        return error, response
