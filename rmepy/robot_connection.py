import socket
import threading
import select
import queue

from . import logger
from .decorators import retry


class RobotConnection(object):
    """
    Create a RobotConnection object with a given robot ip.
    """
    VIDEO_PORT = 40921
    AUDIO_PORT = 40922
    CTRL_PORT = 40923
    PUSH_PORT = 40924
    EVENT_PORT = 40925
    IP_PORT = 40926

    def __init__(self, robot_ip='192.168.2.1'):
        self.robot_ip = robot_ip

        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctrl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.push_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.push_socket.bind((robot_ip, RobotConnection.PUSH_PORT))
        self.ip_socket.bind(('', RobotConnection.IP_PORT))

        self.socket_list = []#[self.push_socket, self.event_socket]
        self.socket_msg_queue = {
            self.video_socket: queue.deque(maxlen=32),
            self.audio_socket: queue.deque(maxlen=32),
            # self.ctrl_socket: queue.Queue(16),
            self.push_socket: queue.deque(maxlen=16),
            self.event_socket: queue.deque(maxlen=16)
        }
        self.socket_recv_thread = threading.Thread(target=self.__socket_recv_task)

        self.running = False
        self.log = logger.Logger(self)

    def __del__(self):
        self.running = False

    def update_robot_ip(self, robot_ip):
        """
        Update the robot ip
        """
        self.robot_ip = robot_ip

    @retry(n_retries=10)
    def get_robot_ip(self, timeout=None):
        """
        Get the robot ip from ip broadcat port

        If optional arg 'timeout' is None (the default), block if necessary until
        get robot ip from broadcast port. If 'timeout' is a non-negative number,
        it blocks at most 'timeout' seconds and return None if no data back from
        robot broadcast port within the time. Otherwise, return the robot ip 
        immediately.
        """
        self.ip_socket.settimeout(timeout)
        msg = None
        try:
            msg, addr = self.ip_socket.recvfrom(1024)
        except Exception as e:
            self.log.warn('Get robot ip failed, please check the robot networking-mode and connection !')
            return False, None
        else:
            msg = msg.decode('utf-8')
            msg = msg[msg.find('robot ip ') + len('robot ip ') : ]
            return True, msg

    @retry(n_retries=50)
    def start(self): 
        """
        Open the connection

        It will connect the control port and event port with TCP and start a data
        receive thread.
        """
        self.ctrl_socket.settimeout(5)

        try:
            self.ctrl_socket.connect((self.robot_ip, RobotConnection.CTRL_PORT))
            # self.event_socket.connect((self.robot_ip, RobotConnection.EVENT_PORT))
        except Exception as e:
            self.log.warn('Connection failed, the reason is %s' %e)
            return False
        else:
            self.running = True
            self.socket_recv_thread.start() 
            self.log.info('Connected to the robot successfully.')
            return True

    @retry()
    def start_video_recv(self):
        if not self.running:
            self.log.error("socket_recv_thread is not running. Try robot_connection.start().")
        if self.video_socket not in self.socket_list:
            self.video_socket.settimeout(5)
            try:
                self.video_socket.connect((self.robot_ip, RobotConnection.VIDEO_PORT))
            except Exception as e:
                self.log.warn('Connection failed, the reason is %s'%e)
                return False
            self.socket_list.append(self.video_socket)
        return True

    def stop_video_recv(self):
        if self.video_socket in self.socket_list:
            self.socket_list.remove(self.video_socket)
        return True

    @retry()
    def start_audio_recv(self):
        if not self.running:
            self.log.error("socket_recv_thread is not running. Try robot_connection.start().")
        if self.audio_socket not in self.socket_list:
            self.audio_socket.settimeout(5)
            try:
                self.audio_socket.connect((self.robot_ip, RobotConnection.AUDIO_PORT))
            except Exception as e:
                self.log.warn('Connection failed, the reason is %s'%e)
                return False
            self.socket_list.append(self.audio_socket)
        return True

    def stop_audio_recv(self):
        if self.audio_socket in self.socket_list:
            self.socket_list.remove(self.audio_socket)
        return True

    @retry()
    def send_msg(self, msg):
        """
        Send msg to control port.
        """
        if not self.running:
            self.log.error("Connection invalid. Try robot_connection.start().")

        try:
            self.ctrl_socket.sendall(msg.encode('utf-8'))
        except socket.error as e:
            self.log.warn("Error at sending '%s': %s" % (msg, e))
            return False, None

        try:
            recv = self.ctrl_socket.recv(4096)
        except socket.error as e:
            self.log.error("Error at receving the response of '%s': %s" % (msg, e))
            return False, None

        return True, recv.decode('utf-8')

    def get_video_data(self, latest_data=False):
        """
        Receive control data

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.

        """
        return self.__get_received_data(self.video_socket, latest_data)

    def get_audio_data(self, latest_data=False):
        """
        Receive control data

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.

        """
        return self.__get_received_data(self.audio_socket, latest_data)

    def get_push_data(self, latest_data=False):
        """
        Receive push data

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.
        """
        return self.__get_received_data(self.push_socket, latest_data)

    def get_event_data(self, latest_data=False):
        """
        Receive event data

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.
        """
        return self.__get_received_data(self.event_socket, latest_data)
        
    def __get_received_data(self, socket_obj, latest_data):
        if not self.running:
            self.log.error("socket_recv_thread is not running. Try robot_connection.start().")
        if not socket_obj in self.socket_list:
            self.log.error("Socket is not running. Try robot_connection.start_XXX_recv().")

        try:
            if latest_data:
                return self.socket_msg_queue[socket_obj][-1]
            return self.socket_msg_queue[socket_obj].pop()
        except Exception as e:
            self.log.warn("Msg queue is empty.")
            return None
        
    def __socket_recv_task(self):
        while self.running:
            rlist, _, _  = select.select(self.socket_list, [], [], 2)

            for s in rlist:
                msg, addr = s.recvfrom(4096)
                self.socket_msg_queue[s].appendleft(msg)

        for s in self.socket_list:
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                pass


# def test():
#     """
#     Test funciton

#     Connect robot and query the version 
#     """
#     robot = RobotConnection('192.168.42.2')
#     robot.start()

#     robot.send_data('command')
#     print('send data to robot   : command')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)

#     robot.send_data('version')
#     print('send data to robot   : version ?')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)

#     robot.send_data('stream on')
#     print('send data to robot   : stream on')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)
#     result = robot.start_video_recv()
#     if result:
#         stream_data = robot.recv_video_data(5)
#         print('recv video data from robot %s'%stream_data)
#         robot.stop_video_recv()
#     robot.send_data('stream off')
#     print('send data to robot   : stream off')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)

#     robot.send_data('audio on')
#     print('send data to robot   : audio on')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)
#     result = robot.start_audio_recv()
#     if result:
#         stream_data = robot.recv_audio_data(5)
#         print('recv audio data from robot %s'%stream_data)
#         robot.stop_audio_recv()
#     robot.send_data('audio off')
#     print('send data to robot   : audio off')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)

#     robot.send_data('quit')
#     print('send data to robot   : quit')
#     recv = robot.recv_ctrl_data(5)
#     print('recv data from robot : %s'%recv)

#     robot.close()


# if __name__ == '__main__':
#     test()