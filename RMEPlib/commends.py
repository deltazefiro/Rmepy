from . import logger


class CmdPkgTemplate(object):
    def __init__(self, robot):
        self.send_cmd = robot.send_cmd
        self.send_query = robot.send_query
        self.log = logger.Logger('Commends')

    def _process_response(self, inp, type_list):
        inp = inp.split(' ')
        out = []
        if type(type_list) == list:
            for data, f in zip(inp, type_list):
                out.append(f(data))
        else:
            out = list(map(type_list, inp))
        return out


class BasicCtrl(CmdPkgTemplate):
    def __init__(self, robot):
        super().__init__(robot)

    def enter_sdk_mode(self):
        """控制机器人进入 SDK 模式

        当机器人成功进入 SDK 模式后，才可以响应其余控制命令

        Args:
            None

        Returns:
            None

        """
        return self.send_cmd('commend')

    def quit_cmd_mode(self):
        """退出 SDK 模式

        控制机器人退出 SDK 模式，重置所有设置项
        Wi-Fi/USB 连接模式下，当连接断开时，机器人会自动退出 SDK 模式

        Args:
            None

        Returns:
            None

        """
        return self.send_cmd('quit')

    def set_robot_mode(self, mode):
        """设置机器人的运动模式

        机器人运动模式描述了云台与底盘之前相互作用与相互运动的关系，
        每种机器人模式都对应了特定的作用关系。

        Args:
            mode (enum): 机器人运动模式
                {0:云台跟随底盘模式, 1:底盘跟随云台模式, 2:自由模式}

        Returns:
            None

        """
        mode_enum = ('chassis_lead', 'gimbal_lead', 'free')
        if mode not in (0, 1, 2):
            self.log.error(
                "Set_chassis_following_mode: 'mode' must be an integer from 0 to 2")
        return self.send_cmd('robot mode ' + mode_enum[mode])

    def get_robot_mode(self):
        """获取机器人运动模式

        查询当前机器人运动模式
        机器人运动模式描述了云台与底盘之前相互作用与相互运动的关系，
        每种机器人模式都对应了特定的作用关系。

        Args:
            None

        Returns:
            (int): 机器人的运动模式
                {0:云台跟随底盘模式, 1:底盘跟随云台模式, 2:自由模式}

        """
        mode_enum = ('chassis_lead', 'gimbal_lead', 'free')
        return mode_enum.index(self.send_cmd('robot mode ?'))


class Chassis(CmdPkgTemplate):
    def __init__(self, robot):
        super().__init__(robot)

    def set_vel(self, speed_x, speed_y, speed_yaw):
        """底盘运动速度控制

        控制底盘运动速度

        Args:
            speed_x (float:[-3.5,3.5]): x 轴向运动速度，单位 m/s
            speed_y (float:[-3.5,3.5]): y 轴向运动速度，单位 m/s
            speed_yaw (float:[-600,600]): z 轴向旋转速度，单位 °/s

        Returns:
            None

        """
        return self.send_cmd('chassis speed x %f y %f z %f' % (speed_x, speed_y, speed_yaw))

    def set_wheel_speed(self, speed_w1, speed_w2, speed_w3, speed_w4):
        """底盘轮子速度控制

        控制四个轮子的速度

        Args:
            speed_w1 (int:[-1000, 1000]): 右前麦轮速度，单位 rpm
            speed_w2 (int:[-1000, 1000]): 左前麦轮速度，单位 rpm
            speed_w3 (int:[-1000, 1000]): 右后麦轮速度，单位 rpm
            speed_w4 (int:[-1000, 1000]): 左后麦轮速度，单位 rpm

        Returns:
            None

        """
        return self.send_cmd('chassis wheel w1 %d w2 %d w3 %d w4 %d' % (speed_w1, speed_w2, speed_w3, speed_w4))

    def shift(self, x=0, y=0, yaw=0, speed_xy=0.5, speed_yaw=90):
        """底盘相对位置控制

        控制底盘运动当指定位置，坐标轴原点为当前位置

        Args:
            x  (float:[-5, 5]): x 轴向运动距离，单位 m
            y  (float:[-5, 5]): y 轴向运动距离，单位 m
            yaw  (int:[-1800, 1800]): z 轴向旋转角度，单位 °
            speed_xy  (float:(0, 3.5]): xy 轴向运动速度，单位 m/s
            speed_yaw  (float:(0, 600]): z 轴向旋转速度， 单位 °/s

        Returns:
            None

        """
        return self.send_cmd('chassis move x %f y %f z %d vxy %f vz %f' % (x, y, yaw, speed_xy, speed_yaw))

    def get_speed(self):
        """底盘速度信息获取

        获取底盘的速度信息

        Args:
            None

        Returns:
            (dict/list) {
                speed_x (float): x轴向的运动速度，单位 m/s 
                speed_y (float): y轴向的运动速度，单位 m/s
                speed_yaw (float): z轴向的旋转速度，单位 °/s
                speed_w1 (int): 右前麦轮速度，单位 rpm
                speed_w2 (int): 左前麦轮速度，单位 rpm
                speed_w3 (int): 右后麦轮速度，单位 rpm
                speed_w4 (int): 左后麦轮速度，单位 rpm
                }


        """
        response = self.send_query('chassis position ?')
        return self._process_response(response, (float, float, float, int, int, int, int))

    def get_postion(self):
        """底盘绝对位置信息获取
        
        获取底盘位置信息
        坐标原点为上电时刻机器人位置
        
        Args:
            None
        
        Returns:
            (dict/list) {
                x (float): x轴向的位移
                y (float): y轴向的位移
                z (float): z轴向的位移
            }
        
        """
        response = self.send_query('chassis position ?')
        return self._process_response(response, float)
    