from .__module_template import  RobotModuleTemplate
from ..decorators import accepts, retry

class BasicCtrl(RobotModuleTemplate):
    def __init__(self, robot):
        super().__init__(robot)

    @retry(n_retries=1e5)
    def enter_sdk_mode(self):
        """控制机器人进入 SDK 模式

        当机器人成功进入 SDK 模式后，才可以响应其余控制命令

        Args:
            None

        Returns:
            None

        """
        resp = self._send_msg('command')[1]
        if resp == 'ok':
            self._log.info('Enter sdk mode successfully.')
            return True
        else:
            self._log.warn('Failed to enter sdk mode: %s' %resp)
            return False

    def quit_cmd_mode(self):
        """退出 SDK 模式

        控制机器人退出 SDK 模式，重置所有设置项
        Wi-Fi/USB 连接模式下，当连接断开时，机器人会自动退出 SDK 模式

        Args:
            None

        Returns:
            None

        """
        return self._send_cmd('quit')

    @accepts((int, 0, 2))
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
        return self._send_cmd('robot mode ' + mode_enum[mode])

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
        return mode_enum.index(self._send_cmd('robot mode ?'))

    def video_stream_on(self):
        """开启视频流推送

        打开视频流
        打开后，可从视频流端口接收到 H.264 编码的码流数据

        Args:
            None

        Returns:
            None

        """
        return self._send_cmd('stream on')

    def video_stream_off(self):
        """关闭视频流推送

        关闭视频流
        关闭视频流后，H.264 编码的码流数据将会停止输出

        Args:
            None

        Returns:
            None

        """
        return self._send_cmd('stream off')
