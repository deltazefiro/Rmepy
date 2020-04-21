from .robot_connection import MsgPushReceiver
from . import logger
import threading


class RobotMsgPush(object):
    def __init__(self, robot, port=40924, socket_time_out=3):
        self.robot = robot
        self.log = logger.Logger(self)
        self.msg_push_receiver = MsgPushReceiver(robot, port, socket_time_out)
        self._receiver_thread = threading.Thread(
            target=self._receiver_thread_task)
        self.running = False
        self._init_attr_dict()

    def __del__(self):
        self.log.info("Shuting down MsgPushReceiver thread...")
        if self.running:
            self.running = False
            self._receiver_thread.join()
            self.log.info(
                'Shutted down MsgPushReceiver thread successfully.')
        else:
            self.log.info(
                'MsgPushReceiver thread has not been started. Skip ...')

    def start(self):
        self.msg_push_receiver.bind()
        self._receiver_thread.start()

    def _receiver_thread_task(self):
        self.running = True
        while self.running:
            msg = self.msg_push_receiver.receiver_task()
            if msg:
                self._process_msg_push(msg)

    def _process_msg_push(self, msg):
        module_name, _, attr, *values = msg.split()
        for key, val in zip(self._attr_dict[module_name][attr], values):
            key = val

    def _init_attr_dict(self):
        # TODO 是有点丑，但目前未能找到更好的选择方式 :(

        robot = self.robot
        self._attr_dict = {

            'chassis': {
                'position': [robot.chassis.x, robot.chassis.y, robot.chassis.z],
                'attitude': [robot.chassis.pitch, robot.chassis.roll, robot.chassis.yaw],
                'status': [robot.chassis.is_static, robot.chassis.is_uphill, robot.chassis.is_downhill, robot.chassis.is_on_slope, robot.chassis.is_pick_up, robot.chassis.is_slip, robot.chassis.is_impact_x, robot.chassis.is_impact_y, robot.chassis.is_impact_z, robot.chassis.is_roll_over, robot.chassis.is_hill_static]
            },

            'gimbal': {
                'attitude': [robot.gimbal.pitch, robot.gimbal.yaw]
            }

        }
