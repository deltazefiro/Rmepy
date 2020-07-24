from . import logger
import threading


class RobotMsgPush(object):
    """ 信息推送接收器

    监听40924端口上的推送信息
    若接到信息，则将不同信息处理加入对应模块的属性中
    信息推送可以通过robot.[robot_module].set_push()设置

    Example:
        # 获取机器人的底盘的位置信息推送
        rm = rmepy.Robot(ip='127.0.0.1')
        ...
        rm.push.start()     # 激活推送接收线程
        rm.chassis.set_push(pos_freq=5)     # 命令机器人推送底盘位置信息
        sleep(1)
        print(rm.chassis.x, rm.chassis.y, rm.chassis.z)     # 调取使用底盘位置信息

    """
    def __init__(self, robot):
        self.robot = robot
        self.log = logger.Logger(self)
        self.get_push_data = robot.connection.get_push_data
        self._receiver_thread = threading.Thread(target=self._receiver_task)
        self.running = False

    def start(self):
        """ 启动 信息推送接收器

        Args:
            None

        Returns:
            None

        """
        self._receiver_thread.start()
        self.log.info("MsgPushReceiver thread started.")

    def _receiver_task(self):
        """信息接收&处理线程

        Args:
            None

        Returns:
            None

        """
        self.running = True
        while self.running and threading.main_thread().is_alive():
            msg = self.get_push_data(timeout=2)
            if msg:
                for idx, m in enumerate(msg.split(';')):
                    if idx == 0:
                        module_name, _, attr, *values = m.split()
                    else:
                        attr, *values = m.split()
                    self._process_msg_push(module_name, attr, values)
        
        self.log.debuginfo('Shutted down RobotMsgPush thread successfully.')
        self.running = False

    def _process_type(self, data, type_list):
        """ 将字符串类型的数据处理成指定类型的数据

        Args:
            data (list/tuple): 要转换的数据
            type_list (list/tuple/type): 目标数据类型
                如果为 type，则将所有的输入数据转为该类型
                若为 list/tuple，且type_list长度必须与data长度一致，所有元素都为 type 类型
                那么将 data 的每个数据转成对应type_list中对应的类型

        Returns:
            (tuple): 转换完的输出

        """
        try:
            if isinstance(type_list, (list, tuple)):
                data = [f(i) if f != bool else bool(int(i))for i, f in zip(data, type_list)]
            else:
                data = [type_list(i) if type_list != bool else bool(int(i)) for i in data]
        except (TypeError, ValueError) as e:
            self.log.warn(
                "Error at processing push msg: %s does not match %s" % (data, type_list))
            data = None
        return data

    def _process_msg_push(self, module_name, attr, values):
        """处理推送信息

        将推送得到的信息转换赋值给对应的robot_modules

        Args:
            module_name (str)
            attr (str)
            values (list/tuple)

        Returns:
            None

        """
        # TODO if-else是有点丑，但目前未能找到更好的选择方式 :(
        robot = self.robot
        if module_name == 'chassis':
            if attr == 'position':
                values = self._process_type(values, float)
                (robot.chassis.x, robot.chassis.y) = values
            elif attr == 'attitude':
                values = self._process_type(values, float)
                (robot.chassis.pitch, robot.chassis.roll, robot.chassis.yaw) = values
            elif attr == 'status':
                values = self._process_type(values, bool)
                (robot.chassis.is_static, robot.chassis.is_uphill, robot.chassis.is_downhill, robot.chassis.is_on_slope, robot.chassis.is_pick_up, robot.chassis.is_slip,
                 robot.chassis.is_impact_x, robot.chassis.is_impact_y, robot.chassis.is_impact_z, robot.chassis.is_roll_over, robot.chassis.is_hill_static) = values
        elif module_name == 'gimbal':
            if attr == 'attitude':
                values = self._process_type(values, float)
                (robot.gimbal.pitch, robot.gimbal.yaw) = values
