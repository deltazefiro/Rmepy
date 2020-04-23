from .__module_template import  RobotModuleTemplate
from ..decorators import accepts

class Gimbal(RobotModuleTemplate):
    def __init__(self, robot):
        super().__init__(robot)

        # attitude
        self.pitch = 0.0
        self.yaw = 0.0

    @accepts((float, -450, 450), (float, -450, 450))
    def set_speed(self, speed_pitch, speed_yaw):
        """云台运动速度控制
        
        控制云台运动速度
        
        Args:
            speed_pitch (float:[-450, 450]): pitch 轴速度，单位 °/s
            speed_yaw (float:[-450, 450]): yaw 轴速度，单位 °/s
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal speed p %s y %s' %(speed_pitch, speed_yaw))
    
    @accepts((float, -55, 55), (float, -55, 55), (float, 0, 540), (float, 0, 540))
    def shift(self, pitch=0., yaw=0., speed_pitch=30., speed_yaw=30.):
        """云台相对位置控制
        
        控制云台运动到指定位置，坐标轴原点为当前位置
        
        Args:
            pitch  (float:[-55, 55]): pitch 轴角度， 单位 °
            yaw  (float:[-55, 55]): yaw 轴角度，单位 °
            speed_pitch  (float:[0, 540]): pitch 轴运动速速，单位 °/s
            speed_yaw  (float:[0, 540]): yaw 轴运动速度，单位 °/s
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal move p %s y %s vp %s vy %s' %(pitch, yaw, speed_pitch, speed_yaw))
    
    @accepts((int, -25, 30), (int, -250, 250), (int, 0, 540), (int, 0, 540))
    def move_to(self, pitch, yaw, speed_pitch, speed_yaw):
        """云台绝对位置控制
        
        控制云台运动到指定位置，坐标轴原点为上电位置
        
        Args:
            pitch  (int:[-25, 30]): pitch 轴角度(°)
            yaw  (int:[-250, 250]): yaw 轴角度(°)
            speed_pitch  (int:[0, 540]): pitch 轴运动速度(°/s)
            speed_yaw  (int:[0, 540]): yaw 轴运动速度(°/s) # TODO 确认是 int 还是 float
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal moveto p %s y %s vp %s vy %s' %(pitch, yaw, speed_pitch, speed_yaw))
    
    def suspend(self):
        """云台休眠控制
        
        控制云台进入休眠状态
        
        Args:
            None
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal suspend')

    def resume(self):
        """云台恢复控制
        
        控制云台从休眠状态中恢复
        
        Args:
            None
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal resume')

    def recenter(self):
        """云台回中控制
        
        控制云台回中
        
        Args:
            None
        
        Returns:
            None
        
        """
        return self.send_cmd('gimbal recenter')

    def get_attitude(self):
        """云台姿态获取
        
        获取云台姿态信息
        
        Args:
            None
        
        Returns:
            (list) [
                pitch (int): pitch 轴角度(°)
                yaw (int): yaw 轴角度(°)
            ]
        
        """
        response = self.send_query('gimbal attitude ?')
        return self._process_response(response, int)
    
    # TODO push msg ctrl