from . import logger


class CmdPkgTemplate(object):
    def __init__(self, robot):
        self.send_cmd = robot.send_cmd
        self.send_query = robot.send_query
        self.log = logger.Logger('Commend')


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
            mode: (enum) 机器人运动模式
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
            mode: (int) 机器人的运动模式
                {0:云台跟随底盘模式, 1:底盘跟随云台模式, 2:自由模式}

        """
        mode_enum = ('chassis_lead', 'gimbal_lead', 'free')
        return mode_enum.index(self.send_cmd('robot mode ?'))



class Chassis(CmdPkgTemplate):
    def __init__(self, robot):
        super().__init__(robot)