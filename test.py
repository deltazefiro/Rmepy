import RMEPlib

rm = RMEPlib.Robot()
rm.connect()
rm.basic_ctrl.enter_sdk_mode()
rm.basic_ctrl.set_robot_mode(2)
rm.chassis.set_vel(1, 2, 3)
print(rm.chassis.get_postion())
print(rm.chassis.get_all_speed())
# while True:
#     cmd = input("Send SDK cmd >> ")
#     rm.send_query(cmd)