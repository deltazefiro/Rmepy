#!/usr/bin/env python3
# coding=utf-8

import queue
import socket
import threading

from . import logger
from .decorators import retry


class CommendSender(object):
    """用于向s1发送控制命令

    Attributes:
        robot: robot对象
        port: 控制命令端口40923

    """

    def __init__(self, robot, port=40923, socket_time_out=3):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(socket_time_out)
        self.log = logger.Logger(self)

    def __del__(self):
        self.log.debuginfo("Shuting down CommendSender ...")
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
        self.log.debuginfo("Connecting to %s:%s ..." % (self.ip, self.port))

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


class VideoStreamReceiver(object):
    def __init__(self, robot, port=40921, time_out=3, recv_buffer_size=32):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.log = logger.Logger(self)
        self.running = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(time_out)
        self.connection = None

        self.recv_buffer = queue.deque(maxlen=recv_buffer_size)
        self._receiver_thread = threading.Thread(
            target=self._receiver_thread_task)

    def __del__(self):
        self.log.debuginfo("Shuting down VideoStreamReceiver ...")
        if self.running:
            self.running = False
            self._receiver_thread.join()
            self.log.debuginfo(
                'Shutted down VideoStreamReceiver thread successfully.')
        else:
            self.log.debuginfo(
                'VideoStreamReceiver thread has not been started. Skip ...')
        self.socket.close()

    def start(self):
        self.robot.basic_ctrl.video_stream_on()
        self.bind()
        self.establish()
        self._receiver_thread.start()
        self.log.info("VideoStream thread started.")
        self.running = True

    @retry(n_retries=3)
    def bind(self):
        self.log.debuginfo("Binding to %s:%s ..." % (self.ip, self.port))
        try:
            self.socket.bind((self.ip, self.port))
        except socket.error as e:
            self.log.error("Fail to bind VideoStream port. Error: %s" % e)
            return False
        else:
            self.log.debuginfo("VideoStream port bound.")
            return True

    @retry(n_retries=3)
    def establish(self):
        self.socket.listen()
        try:
            self.connection, _ = self.socket.accept()
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
                    self.recv_buffer.appendleft(data)
                elif self.running:
                    self.log.error("Got a null msg from the video stream.")
            except socket.timeout:
                if self.running:
                    self.log.warn(
                        "Nothing has been received from VideoStream port. (timeout)")


class MsgPushReceiver(object):
    def __init__(self, robot, port=40924, time_out=3):
        self.robot = robot
        self.ip = robot.ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(time_out)
        self.log = logger.Logger(self)
        # self.running = False
        # self._receiver_thread = threading.Thread(
        #     target=self._receiver_thread_task)

    def __del__(self):
        self.socket.close()

    # def start(self):
    #     self.bind()
    #     # self._receiver_thread.start()
    #     self.log.info('PushDataReceiver thread started.')

    @retry(n_retries=3)
    def bind(self):
        self.log.debuginfo("Binding to %s:%s ..." % (self.ip, self.port))
        try:
            self.socket.bind((self.ip, self.port))
        except socket.error as e:
            self.log.warn("Fail to bind Push port. Error: %s" % e)
            return False
        else:
            self.log.debuginfo("Push port bound.")
            return True

    def receiver_task(self):
        try:
            return self.socket.recv(4096).decode('utf-8')
            # self.robot.push_buffer.appendleft()
        except socket.timeout:
            return None
        except socket.error as e:
            self.log.error("Error at decoding: %s" % e)
            return None
