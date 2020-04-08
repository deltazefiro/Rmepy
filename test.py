import RMEPlib

rm = RMEPlib.Robot()
rm.connect()
rm.basic_ctrl.enter_sdk_mode()
rm.basic_ctrl.set_robot_mode(2)
# while True:
#     cmd = input("Send SDK cmd >> ")
#     rm.send_query(cmd)