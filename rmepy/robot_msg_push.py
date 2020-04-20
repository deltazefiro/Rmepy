from .robot_connection import MsgPushReceiver
import threading

class RobotMsgPush(object):
    def __init__(self, robot, port=40924, socket_time_out=3):
        self.robot = robot
        self.msg_push_receiver = MsgPushReceiver(robot, port, socket_time_out)
        self._receiver_thread = threading.Thread(target=self._receiver_thread_task)
        self.running = False

    def __del__(self):
        self.running = False
        self.log.info("Shuting down MsgPushReceiver thread...")
        if self.running:
            self._receiver_thread.join()
            self.log.info(
                'Shutted down MsgPushReceiver thread successfully.')
        else:
            self.log.info(
                'MsgPushReceiver thread has not been started. Skip ...')

    def start(self):
        pass

    def _receiver_thread_task(self):
        pass