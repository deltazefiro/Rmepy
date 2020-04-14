# RMEPlib

RMEPlib 是一个对接 RobomasterEP官方sdk 的 python接口，目标是还原官方在robomaster app中封装的python接口。



### Caution:

本项目仍在开发中，代码可能并不完整

并且因为疫情原因并未经过实际测试，并未经过实际测试

若对您的机器人造成损害，恕不负责



### Usage:

1. git clone git@github.com:233a344a455/RMEPlib.git 克隆本项目代码
2. 编译官方提供的 [h264decoder](https://github.com/dji-sdk/RoboMaster-SDK/tree/master/sample_code/RoboMasterEP/stream/decoder)，将编译得到的两个.so文件放入 RMEPlib/
3. 在 clone 的位置下创建 脚本文件，可用以下代码测试

```python
import RMEPlib
from time import sleep

rm = RMEPlib.Robot()
rm.connect()
rm.basic_ctrl.enter_sdk_mode()
sleep(1)
rm.basic_ctrl.set_robot_mode(2)
rm.chassis.set_vel(0, 1, 10)
sleep(1)
rm.chassis.set_vel(0, 0, 0)
print(rm.chassis.get_postion())
print(rm.chassis.get_all_speed())
```



### TODOs:

- [x]  发送控制命令
- [x]  接收s1的状态推送
- [ ]  对s1的状态推送信息进行处理
- [ ]  封装一些基本的控制命令（已完成chassis和basic_ctrl模块）
- [ ]  接收s1的视频流