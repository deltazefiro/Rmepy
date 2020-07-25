
# python3 -i path/to/project/interact.py

import rmepy

rm = rmepy.Robot()
rm.start()
print(rm.send_msg('SDK version: ')[1])

def send_raw():
    print("Enter send raw command mode.")
    while True:
        i = input(' > ')
        if i == 'e':
            return
        print(rm.send_msg(i))
    print("Exit send raw command mode.")