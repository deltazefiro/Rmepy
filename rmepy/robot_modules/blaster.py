from .__module_template import  RobotModuleTemplate
from ..decorators import accepts

class Blaster(RobotModuleTemplate):
    def __init__(self, robot):
        super().__init__(robot)

        self.bullet_num = 0 # 子弹数量（可能不准确）
        self.__n_repeat = 0 # 发生器目前的单次发射水弹数量

    accepts(int)
    def set_bullet_num(self, bullet_num):
        """设置剩余子弹数量
        
        设置弹仓中的子弹数量
        用于估计子弹余量
        
        Args:
            bullet_num (int): 弹仓中的子弹数量
        
        Returns:
            None
        
        """
        self.bullet_num = bullet_num
        return None
        
    accepts((int, 1, 5))
    def fire(self, n_repeat):
        """控制发射器发射子弹
        
        控制水弹枪发射进行发射
        
        Args:
            n_repeat (int:[1, 5]): 连发子弹数
        
        Returns:
            None
        
        """
        if not self.__n_repeat == n_repeat:
            self._send_cmd('blaster bead %d' %n_repeat)
            self.__n_repeat = n_repeat
        return self._send_cmd('blaster fire')
        