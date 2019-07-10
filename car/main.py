from __future__ import print_function
import os
import time

import pygame
import RPi.GPIO as GPIO

CHANNEL_LEFT = 4
CHANNEL_RIGHT = 17
CHANNEL_FORWARD = 27
CHANNEL_REVERSE = 22

# Must be between 0 and 100
FORWARD_SPEED = 50


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
        GPIO.output(CHANNEL_REVERSE, 1)
        self._forward_pwm.ChangeDutyCycle(FORWARD_SPEED)

    def stop(self):
        self._forward_pwm.ChangeDutyCycle(100)
        GPIO.output(CHANNEL_FORWARD, 1)
        GPIO.output(CHANNEL_REVERSE, 1)

    def reverse(self):
        self._forward_pwm.ChangeDutyCycle(100)
        GPIO.output(CHANNEL_FORWARD, 1)
        GPIO.output(CHANNEL_REVERSE, 0)

    def shutdown(self):
        self._forward_pwm.stop()
        GPIO.cleanup()

    def _init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        for channel in (CHANNEL_LEFT, CHANNEL_RIGHT,
                        CHANNEL_FORWARD, CHANNEL_REVERSE):
            GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
        self._forward_pwm = GPIO.PWM(CHANNEL_FORWARD, 10)
        self._forward_pwm.start(100)

    def _set_left_right(self, left, right):
        assert left | right, 'Cannot steer both left and right simultaneously.'
        if left:
            GPIO.output(CHANNEL_LEFT, left)
            GPIO.output(CHANNEL_RIGHT, right)
        else:
            GPIO.output(CHANNEL_RIGHT, right)
            GPIO.output(CHANNEL_LEFT, left)


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
