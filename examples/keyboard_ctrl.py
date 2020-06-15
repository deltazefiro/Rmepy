
"""
使用键盘控制机器人
    - a/s/d/f: 移动
    - q/e: 转向
"""

import sys
import os
import numpy as np
import pygame
import time

# add parent directory to import path
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
import rmepy

MOVE_SPEED = 0.5
ROTATE_SPEED = 20
CMD_SEND_FREQ = 5

running = True
r = rmepy.Robot()
r.start()
r.video.start()
time.sleep(0.1)

def key_handler(k):
    global running, r, speed
    if k[pygame.K_w]:
        # forward
        speed = (MOVE_SPEED, 0, 0)
    if k[pygame.K_s]:
        # back
        speed = (-MOVE_SPEED, 0, 0)
    if k[pygame.K_d]:
        # right
        speed = (0, MOVE_SPEED, 0)
    if k[pygame.K_f]:
        # left
        speed = (0, -MOVE_SPEED, 0)
    if k[pygame.K_q]:
        # counter clockwise rotate
        speed = (0, 0, ROTATE_SPEED)
    if k[pygame.K_e]:
        # clockwise rotate
        speed = (0, 0, -ROTATE_SPEED)

def ctrl_thread():
    while running:
        r.chassis.set_speed(speed)
        time.sleep(1/CMD_SEND_FREQ)

if __name__ == "__main__":
    pygame.init()

    display = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    while running:

        speed = (0, 0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        key_handler(keys)

        # Draw image
        temp = r.video.get_frame()
        if temp is not None:
            frame = temp
        pygame.surfarray.blit_array(display, frame)
        pygame.display.flip()

        clock.tick(30)

    pygame.quit()