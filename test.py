import rmepy

rm = rmepy.Robot(ip='127.0.0.1')
rm.connect()
rm.basic_ctrl.enter_sdk_mode()


rm.basic_ctrl.set_robot_mode(2)
rm.chassis.set_vel(1., 2., 3.)
print(rm.chassis.get_postion())
print(rm.chassis.get_all_speed())
rm.chassis.set_wheel_speed(34, 123, 11, 11)
rm.video.start()
while True:
    cmd = input("Send SDK cmd >> ")
    rm.send_query(cmd)
