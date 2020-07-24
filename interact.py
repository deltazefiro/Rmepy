import rmepy

rm = rmepy.Robot()
rm.start()
print(rm.send_msg('version')[1])

def send():
    while True:
        i = input('> ')
        if i == 'e':
            return
        print(rm.send_msg(i))