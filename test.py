import RMEPlib

rm = RMEPlib.Robot()
rm.connect()
while True:
    cmd = input("Send SDK cmd >> ")
    rm.send_query(cmd)