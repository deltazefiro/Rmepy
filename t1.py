import evdev
import threading

def scale(val, src, dst=(-100, 100)):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

print("Finding controller...")
devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
    if device.name == 'GamepadPlus V3':
        ps3dev = device.fn

gamepad = evdev.InputDevice(ps3dev)

print('start!')

speed = 0
running = True

for event in gamepad.read_loop():
    if event.type == 3:
        if event.code == 53:
            fb = scale(event.value, (114 ,396))
        if event.code == 54:
            rl = scale(event.value, (129, 420))
        if event.code == 57:
            fb = rl = 0.

    
    print('fb = %.2f, rl = %.2f' % (fb, rl))

    # if event.type == 1 and event.code == 330 and event.value == 1:
    #     print("X button is pressed. Stopping.")
    #     running = False
    #     break