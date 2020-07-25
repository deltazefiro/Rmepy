# Rmepy

Rmepy 是一个对接RobomasterEP sdk的非官方python3接口，目标是还原官方在robomaster app中封装的python接口。



### Features:

该项目目前提供以下功能

- 提供使用 python3 封装的 robomasterEP sdk，允许直接在程序中调用 sdk

  ```python
  # Example
  rm.start()
  rm.basic_ctrl.set_robot_mode(2)
  rm.chassis.set_speed(0.0, 0.0, 10.0)
  ```

- 对机器人传来的视频流进行接收和解码

  ```python
  # Example
  rm.video.start()
  rm.video.display()
  ```
  
- 对机器人的推送信息进行处理，能在程序中调用

  ```python
  # Example
  rm.push.start()
  rm.gimbal.set_push(atti_freq=5)
  print(rm.gimbal.pitch, rm.gimbal.yaw)
  ```



### Requirements:

- 控制端
  - Python3 (测试使用python3.6&3.8)
  - opencv-python
  - numpy
  - pillow (PIL)
  - [h264decoder](https://github.com/dji-sdk/RoboMaster-SDK/tree/master/sample_code/RoboMasterEP/stream/decoder)

- 机器人
  - EP版本  v01.00.00.00
  - 明文 SDK 版本 v00.00.00.32



### Usage:

1. 从Pypi安装本项目:

   ```bash
   pip3 install rmepy
   ```

2. **根据自己的操作系统手动安装 [h264decoder](https://github.com/dji-sdk/RoboMaster-SDK/tree/master/sample_code/RoboMasterEP/stream/decoder)**

3. Enjoy! 可以使用以下代码进行测试


```python
import rmepy
from time import sleep

r = rmepy.Robot()
r.start()

r.video.log.level = 'WARNING'
r.video.log.level = 'INFO'

r.video.start()
r.video.display()

r.basic_ctrl.set_robot_mode(2)
r.chassis.set_push(1, 1, 1)
r.chassis.set_speed(0.0, 1.0, 10.0)
print(r.chassis.get_postion())
sleep(1)
r.chassis.set_speed(0.0, 0.0, 0.0)
print(r.chassis.get_postion())
sleep(1e5)
```

目前支持的其他命令的详细内容

可以使用 help(rmepy.robot_modules) 或 进入 rmepy/robot_modules 查看



### Project structure:

文件结构

```
rmepy
├── decorators.py	# 装饰器，包括 retry, accepts 等
├── __init__.py
├── logger.py	# 提供日志输出服务
├── robot_connection.py		# 提供与机器人的通讯服务
├── robot_modules	# 封装的sdk命令
│   ├── basic_ctrl.py	# 基础操控
│   ├── chassis.py	# 底盘控制
│   ├── gimbal.py	# 云台控制
│   ├── blaster.py	# 发射器控制
│   ├── __init__.py
│   └── __module_template.py
├── robot_msg_push.py	# 信息推送流处理
├── robot.py	# 主类(rmepy.Robot)
└── robot_video_stream.py	# 视频流处理
```

类结构

``` 
rmepy.Robot

        # Commends 封装的命令
        .basic_ctrl = commends.BasicCtrl()
        .chassis = commends.Chassis()
        .gimbal = commends.Gimbal()
        .blaster = robot_modules.Blaster()
        
        # Video 基础视频模块
        .video = robot_video_stream.RobotVideoStream()
        
        # Push 推送信息处理模块
        .push = robot_msg_push.RobotMsgPush()
```



### TODOs:

- [x]  发送控制命令
- [x]  接收s1的状态推送
- [x]  对s1的状态推送信息进行处理
- [ ]  封装所有基本的控制命令
- [x]  接收s1的视频流
- [x]  对状态推送信息处理进行测试
- [x] 对视频流接收进行测试
- [ ] 增加 advanced 模块，进行图像的高级处理（巡线，yolov3的物体识别等）

