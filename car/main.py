from __future__ import print_function
import os
import time

import pygame
import RPi.GPIO as GPIO

CHANNEL_LEFT = 4
CHANNEL_RIGHT = 17
CHANNEL_FORWARD = 27
CHANNEL_REVERSE = 22


class Car(object):

    def __init__(self):
        self._init_gpio()

    def left(self):
        self._set_left_right(0, 1)

    def straight(self):
        self._set_left_right(1, 1)

    def right(self):
        self._set_left_right(1, 0)

    def forward(self):
        self._set_forward_reverse(0, 1)

    def stop(self):
        self._set_forward_reverse(1, 1)

    def reverse(self):
        self._set_forward_reverse(1, 0)

    def shutdown(self):
        GPIO.cleanup()

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        for channel in (CHANNEL_LEFT, CHANNEL_RIGHT,
                        CHANNEL_FORWARD, CHANNEL_REVERSE):
            GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)

    def _set_left_right(self, left, right):
        assert left | right, 'Cannot steer both left and right simultaneously.'
        if left:
            GPIO.output(CHANNEL_LEFT, left)
            GPIO.output(CHANNEL_RIGHT, right)
        else:
            GPIO.output(CHANNEL_RIGHT, right)
            GPIO.output(CHANNEL_LEFT, left)

    def _set_forward_reverse(self, forward, reverse):
        assert forward | reverse, 'Cannot forward and reverse simulatenously.'
        if forward:
            GPIO.output(CHANNEL_FORWARD, forward)
            GPIO.output(CHANNEL_REVERSE, reverse)
        else:
            GPIO.output(CHANNEL_REVERSE, reverse)
            GPIO.output(CHANNEL_FORWARD, forward)


def main():
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    pygame.display.init()

    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    car = Car()

    print('Entering event loop, press CTRL+C to quit')
    try:
        while True:
            pygame.event.wait()
            _ = pygame.event.get()
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            print('\rx={:.2f}, y={:.2f}'.format(x, y), end='')
            if x <= -.5:
                car.left()
            elif x >= .5:
                car.right()
            else:
                car.straight()
            if y <= -.3:
                car.forward()
            elif y >= .3:
                car.reverse()
            else:
                car.stop()
    except KeyboardInterrupt:
        pass
    finally:
        car.shutdown()


if __name__ == '__main__':
    main()
