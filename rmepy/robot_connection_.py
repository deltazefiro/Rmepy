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
        self.running = False
        self.log = logger.Logger(self)

        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctrl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.push_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.push_socket.bind(('', RobotConnection.PUSH_PORT))
            self.ip_socket.bind(('', RobotConnection.IP_PORT))
        except OSError as e:
            self.log.error('Error when binding ports: %s' %e)

        self.socket_list = [self.push_socket, self.event_socket]
        self.socket_msg_queue = {
            self.video_socket: queue.Queue(maxsize=32),
            self.audio_socket: queue.Queue(maxsize=32),
            self.push_socket: queue.Queue(maxsize=16),
            self.event_socket: queue.Queue(maxsize=16)
        }
        self.socket_recv_thread = threading.Thread(target=self._socket_recv_task)

    def __del__(self):
        for s in self.socket_list:
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception as e:
                pass

    def update_robot_ip(self, robot_ip):
        """
        Update the robot ip
        """
        self.robot_ip = robot_ip

    @retry(n_retries=10)
    def get_robot_ip(self, timeout=None):
        """
        Get the robot ip from ip broadcast port

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
            self.event_socket.connect((self.robot_ip, RobotConnection.EVENT_PORT))
        except Exception as e:
            self.log.warn('Connection failed: %s' %e)
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
                self.log.warn('Video connection failed: %s'%e)
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
                self.log.warn('Audio connection failed:  %s'%e)
                return False
            self.socket_list.append(self.audio_socket)
        return True

    def stop_audio_recv(self):
        if self.audio_socket in self.socket_list:
            self.socket_list.remove(self.audio_socket)
        return True

    def send_msg(self, msg):
        """
        Send msg to control port.
        """
        if not self.running:
            self.log.error("Connection invalid. Try robot_connection.start().")
            return False, None

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
        
        return True, recv.decode('utf-8').strip(' ;')

    @retry(n_retries=3)
    def send_cmd(self, cmd):
        """Send a commend which does not require returns.

        向s1发送一个不需要返回值的命令
        即若执行成功s1只返回'ok'的命令，如 'connect' 命令

        Args:
            cmd: (str) 命令

        Returns:
            (succ: (bool) 是否成功，被修饰器使用)
            None
        """
        # succ, response = self.send_msg(cmd + ';')
        succ, response = self.send_msg(cmd)
        if succ:
            if response == 'ok':
                self.log.info("'%s' recevied 'ok'." % cmd)
                return True
            elif response == '':
                self.log.warn("Got null response of '%s'." % cmd)
            else:
                self.log.warn("Received an error when executing '%s': %s" % (cmd, response))
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
        succ, response = self.send_msg(cmd)
        # succ, response = self.send_msg(cmd + ';')

        if succ:
            if response == '':
                self.log.warn("Got null response of '%s'." % cmd)
            else:
                self.log.info("'%s' received '%s'." % (cmd, response))
                return True, response

        return False, None

    def get_video_data(self, latest_data=False):
        """
        Get video data from received msg queue

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.

        """
        return self._get_received_data(self.video_socket, latest_data)

    def get_audio_data(self, latest_data=False):
        """
        Get audio data from received msg queue

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.

        """
        return self._get_received_data(self.audio_socket, latest_data)

    def get_push_data(self, latest_data=False):
        """
        Get push msg from received msg queue

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.
        """
        data =  self._get_received_data(self.push_socket, latest_data)
        if data:
            return data.decode('utf-8').strip(' ;')
        else:
            return None

    def get_event_data(self, latest_data=False):
        """
        Get event data from received msg queue

        If optional arg 'latest_data' is set to True, it will return the latest
        data, instead of the data in queue tail.
        """
        data = self._get_received_data(self.event_socket, latest_data)
        if data:
            return data.decode('utf-8').strip(' ;')
        else:
            return None

    def _get_received_data(self, socket_obj, latest_data):
        if not self.running:
            self.log.error("socket_recv_thread is not running. Try robot_connection.start().")
        if not socket_obj in self.socket_list:
            self.log.error("Socket is not running. Try robot_connection.start_XXX_recv().")

        try:
            if latest_data:
                return self.socket_msg_queue[socket_obj][-1]
            return self.socket_msg_queue[socket_obj].get(timeout=2)
        except Exception as e:
            # self.log.debuginfo("Msg queue is empty.")
            return None
        
    def _socket_recv_task(self):
        while self.running and threading.main_thread().is_alive():
            rlist, _, _  = select.select(self.socket_list, [], [], 2)

            for s in rlist:
                msg, addr = s.recvfrom(4096)
                if self.socket_msg_queue[s].full():
                    self.socket_msg_queue[s].get()
                self.socket_msg_queue[s].put(msg)
        
        self.log.debuginfo('Shutted down SocketRecv thread successfully.')
        self.running = False
