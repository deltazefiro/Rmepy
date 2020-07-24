from .__module_template import  RobotModuleTemplate
from ..decorators import accepts

class Chassis(RobotModuleTemplate):
    def __init__(self, robot):
        super().__init__(robot)

        # position 底盘当前的位置距离上电时刻位置
        self.x = 0.0  # x 轴位置(m)
        self.y = 0.0  # y 轴位置(m)

        # attitude
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0

        # status
        self.is_static = False  #是否静止
        self.is_uphill = False  #是否上坡
        self.is_downhill  = False  #是否下坡
        self.is_on_slope = False  #是否溜坡
        self.is_pick_up  = False  #是否被拿起
        self.is_slip  = False  #是否滑行
        self.is_impact_x  = False  #x 轴是否感应到撞击
        self.is_impact_y = False  #y 轴是否感应到撞击
        self.is_impact_z = False  #z 轴是否感应到撞击
        self.is_roll_over = False  #是否翻车
        self.is_hill_static = False #是否在坡上静止

    @accepts(speed_x=(float, -3.5, 3.5), speed_y=(float, -3.5, 3.5), speed_yaw=(float, -600, 600))
    def set_speed(self, speed_x, speed_y, speed_yaw):
        """底盘运动速度控制

        控制底盘运动速度

        Args:
            speed_x (float:[-3.5,3.5]): x 轴向运动速度，单位 m/s
            speed_y (float:[-3.5,3.5]): y 轴向运动速度，单位 m/s
            speed_yaw (float:[-600,600]): z 轴向旋转速度，单位 °/s

        Returns:
            None

        """
        return self._send_cmd('chassis speed x %f y %f z %f' % (speed_x, speed_y, speed_yaw))

    @accepts((int, -1000, 1000), (int, -1000, 1000), (int, -1000, 1000), (int, -1000, 1000))
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
        return self._send_cmd('chassis wheel w1 %d w2 %d w3 %d w4 %d' % (speed_w1, speed_w2, speed_w3, speed_w4))

    @accepts((float, -5, 5), (float, -5, 5), (int, -1800, 1800), (float, 0, 3.5), (float, 0, 600))
    def shift(self, x=0., y=0., yaw=0, speed_xy=0.5, speed_yaw=90.):
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
        return self._send_cmd('chassis move x %f y %f z %d vxy %f vz %f' % (x, y, yaw, speed_xy, speed_yaw))

    def get_all_speed(self):
        """底盘速度信息获取

        获取底盘的速度信息

        Args:
            None

        Returns:
            (list) [
                speed_x (float): x轴向的运动速度，单位 m/s 
                speed_y (float): y轴向的运动速度，单位 m/s
                speed_yaw (float): z轴向的旋转速度，单位 °/s
                speed_w1 (int): 右前麦轮速度，单位 rpm
                speed_w2 (int): 左前麦轮速度，单位 rpm
                speed_w3 (int): 右后麦轮速度，单位 rpm
                speed_w4 (int): 左后麦轮速度，单位 rpm
                ]


        """
        response = self._send_query('chassis speed ?')
        return self._process_response(response, (float, float, float, int, int, int, int))

    def get_speed(self):
        """获取机器人运动速度

        获取机器人整体的速度信息

        Args:
            None

        Returns:
            (list) [
                speed_x (float): x轴向的运动速度，单位 m/s 
                speed_y (float): y轴向的运动速度，单位 m/s
                speed_yaw (float): z轴向的旋转速度，单位 °/s
                ]

        """
        return self.get_all_speed()[:3]

    def get_wheel_speed(self):
        """获取麦轮速度

        获取麦轮的速度信息

        Args:
            None

        Returns:
            (list) [
                speed_w1 (int): 右前麦轮速度，单位 rpm
                speed_w2 (int): 左前麦轮速度，单位 rpm
                speed_w3 (int): 右后麦轮速度，单位 rpm
                speed_w4 (int): 左后麦轮速度，单位 rpm
                ]

        """
        return self.get_all_speed()[3:]

    def get_postion(self):
        """底盘位置信息获取

        获取底盘的位置信息
        上电时刻机器人所在的位置为坐标原点

        Args:
            None

        Returns:
            (list) [
                x (float): x轴向的位移
                y (float): y轴向的位移
                z (float): z轴向的位移
            ]

        """
        response = self._send_query('chassis position ?')
        return self._process_response(response, float)

    def get_attitude(self):
        """获取底盘姿态信息

        查询底盘的姿态信息

        Args:
            None

        Returns:   #TODO:确定返回值为 int 还是 float
            (list) [
                pitch (float): pitch 轴角度，单位 °
                roll (float): roll 轴角度，单位 °
                yaw (float): yaw 轴角度，单位 °
            ]

        """
        response = self._send_query('chassis attitude ?')
        return self._process_response(response, float)

    def get_status(self):
        """获取底盘状态信息

        获取底盘状态信息

        Args:
            None

        Returns:
            (list) [
                static (bool): 是否静止
                uphill (bool): 是否上坡
                downhill (bool): 是否下坡
                on_slope (bool): 是否溜坡
                pick_up (bool): 是否被拿起
                slip (bool): 是否滑行
                impact_x (bool): x 轴是否感应到撞击
                impact_y (bool): y 轴是否感应到撞击
                impact_z (bool): z 轴是否感应到撞击
                roll_over (bool): 是否翻车
                hill_static (bool): 是否在坡上静止
            ]

        """
        response = self._send_query('chassis status ?')
        return self._process_response(response, bool)

    def set_push(self, pos_freq=None, atti_freq=None, status_freq=None):
        """底盘信息推送控制
        
        打开/关闭底盘中相应属性的信息推送与频率设置
        若已使用 Robot.push.start 激活推送接收器
        可以直接从 Robot.chassis.[属性名] 获取推送信息

        Args:
            支持的频率 1, 5, 10, 20, 30, 50
            频率为 0 则关闭该属性推送
            若输入为 None 则不改变该属性的推送评论

            pos_freq (int/None)
            atti_freq (int/None)
            status_freq (int/None)
        
        Returns:
            None
        
        """

        if pos_freq == atti_freq == status_freq == None:
            self._log.warn("set_push: got 3 None args." )
            return False
        else:
            cmd = 'chassis push'
            if pos_freq == None:
                pass
            elif pos_freq == 0:
                cmd += ' position off'
            elif pos_freq in (1, 5, 10, 20, 30, 50):
                cmd += ' position on pfreq %d' %pos_freq
            else:
                self._log.error("set_push: 'pos_freq' should be an integer in (0, 1, 5, 10, 20, 30, 50), but got %r" %pos_freq)
            
            if atti_freq == None:
                pass
            elif atti_freq == 0:
                cmd += ' attitude off'
            elif atti_freq in (1, 5, 10, 20, 30, 50):
                cmd += ' attitude on afreq %d' %atti_freq
            else:
                self._log.error("set_push: 'atti_freq' should be an integer in (0, 1, 5, 10, 20, 30, 50), but got %r" %atti_freq)

            if status_freq == None:
                pass
            elif status_freq == 0:
                cmd += ' status off'
            elif status_freq in (1, 5, 10, 20, 30, 50):
                cmd += ' status on sfreq %d' %status_freq
            else:
                self._log.error("set_push: 'status_freq' should be an integer in (0, 1, 5, 10, 20, 30, 50), but got %r" %status_freq)

            return self._send_cmd(cmd)