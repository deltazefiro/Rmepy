import rmepy
from time import sleep

rm = rmepy.Robot(ip='127.0.0.1')
rm.connect()
rm.basic_ctrl.enter_sdk_mode()
sleep(1)
rm.basic_ctrl.set_robot_mode(2)
rm.chassis.set_vel(0.0, 1.0, 10.0)
sleep(1)
rm.chassis.set_vel(0.0, 0.0, 0.0)
print(rm.chassis.get_postion())
print(rm.chassis.get_all_speed())

rm.push.start()
rm.gimbal.set_push(atti_freq=5)
sleep(0.5)
print(rm.gimbal.pitch, rm.gimbal.yaw)

rm.video.start()
sleep(1)
rm.video.display()
sleep(10)