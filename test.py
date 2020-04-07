import RMEPlib

rm = RMEPlib.RMEP()
rm.connect()
while True:
    cmd = input("Send SDK cmd >> ")
    rm.send_query(cmd)