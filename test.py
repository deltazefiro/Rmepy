import RMEPlib

rm = RMEPlib.Robot(ip='127.0.0.1')
rm.connect()
rm.basic_ctrl.enter_sdk_mode()

# rm.video.start()

rm.basic_ctrl.set_robot_mode(4)
rm.chassis.set_vel(1, 2, 3)
print(rm.chassis.get_postion())
print(rm.chassis.get_all_speed())
rm.chassis.set_wheel_speed(1234, 123, 11, 11)
while True:
    cmd = input("Send SDK cmd >> ")
    rm.send_query(cmd)
