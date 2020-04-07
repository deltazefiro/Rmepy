from . import Logger

class CmdPkgTemplate(object):
    def __init__(self, robot):
        self.send_cmd = robot.send_cmd
        self.send_query = robot.send_query
        self.log = Logger.logger('Commend')

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
    
    def quit_sdk_mode(self):
        """控制机器人退出 SDK 模式，重置所有设置项

        Wi-Fi/USB 连接模式下，当连接断开时，机器人会自动退出 SDK 模式

        Args:
            None
        
        Returns:
            None
        """
        