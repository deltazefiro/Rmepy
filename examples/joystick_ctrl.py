
# Control the robot with joystick.
# Not finished yet.

import os
import sys
import threading
import time

import evdev
import numpy as np
import pygame

# add parent directory to import path
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
import rmepy

MOVE_SPEED = 1.5
ROTATE_SPEED = 400
CMD_SEND_FREQ = 30

running = True
r = rmepy.Robot()
r.start()
r.video.start()
time.sleep(0.1)
r.video.log.level = 'INFO'
r.connection.log.level = 'WARNING'

def scale(val, src, dst=(-1, 1)):
    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

speed = [0, 0, 0]

def key_handler(k):
    global running, r, speed, l_pos, z
    speed[:2] = 0, 0
    if k[pygame.K_w]:
        # forward
        speed[0] = MOVE_SPEED
    if k[pygame.K_s]:
        # back
        speed[0] = -MOVE_SPEED
    if k[pygame.K_d]:
        # right
        speed[1] = -MOVE_SPEED
    if k[pygame.K_a]:
        # left
        speed[1] = MOVE_SPEED
    if k[pygame.K_ESCAPE]:
        # exit
        running = False
        
def ctrl_task():
    global speed
    while running:
        r.chassis.set_speed(*speed)
        time.sleep(1/CMD_SEND_FREQ)
        print(speed)

def read_joystick_task():
    global speed, running

    for event in gamepad.read_loop():
        if event.type == 3:
            if event.code == 53:
                fb = scale(event.value, (114 ,396))
            if event.code == 54:
                rl = scale(event.value, (129, 420))
            if event.code == 57:
                fb = rl = 0.
        
        speed[2] = -ROTATE_SPEED * rl

        if not running:
            break


if __name__ == "__main__":

    print("Finding controller...")
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for device in devices:
        if device.name == 'GamepadPlus V3':
            ps3dev = device.fn

    gamepad = evdev.InputDevice(ps3dev)

    print('start!')

    ctrl_thread = threading.Thread(target=ctrl_task)
    ctrl_thread.start()
    read_joystick_thread = threading.Thread(target=read_joystick_task)
    read_joystick_thread.start()

    pygame.init()

    display = pygame.display.set_mode((1080, 720))
    clock = pygame.time.Clock()

    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        key_handler(keys)

        # Draw image
        temp = r.video.get_frame()
        if temp is not None:
            frame = np.rot90(temp, 1)
        surf = pygame.surfarray.make_surface(frame)
        display.blit(surf, (0, 0))
        pygame.display.flip()

        clock.tick(65)

    pygame.quit()
