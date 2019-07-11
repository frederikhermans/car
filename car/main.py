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
        self._max_forward_speed = 1.0
        self._max_reverse_speed = 1.0

        # Set up GPIO pins and pulse width modulators (PWMs)
        GPIO.setmode(GPIO.BCM)
        for channel in (CHANNEL_LEFT, CHANNEL_RIGHT,
                        CHANNEL_FORWARD, CHANNEL_REVERSE):
            GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
        self._forward_pwm = GPIO.PWM(CHANNEL_FORWARD, 10)
        self._forward_pwm.start(100)
        self._reverse_pwm = GPIO.PWM(CHANNEL_REVERSE, 10)
        self._reverse_pwm.start(100)

    def set_direction(self, direction):
        assert -1 <= direction and direction <= 1, 'Direction must be between -1 and 1.'

        steer_left = direction <= -.4
        steer_right = direction >= .4

        if steer_left:
            # Pins are active low, so we output `not steer_x`
            GPIO.output(CHANNEL_RIGHT, not steer_right)
            GPIO.output(CHANNEL_LEFT, not steer_left)
        else:
            GPIO.output(CHANNEL_LEFT, not steer_left)
            GPIO.output(CHANNEL_RIGHT, not steer_right)

    def set_speed(self, speed):
        assert -1 <= speed and speed <= 1, 'Speed must be between -1 and 1.'
        if speed >= 0:
            self._reverse_pwm.ChangeDutyCycle(100)
            GPIO.output(CHANNEL_REVERSE, 1)
            self._forward_pwm.ChangeDutyCycle(
                self._dutycycle(speed * self._max_forward_speed))
        else:
            self._forward_pwm.ChangeDutyCycle(100)
            GPIO.output(CHANNEL_FORWARD, 1)
            self._reverse_pwm.ChangeDutyCycle(
                self._dutycycle(-speed * self._max_reverse_speed))

    def shutdown(self):
        self._forward_pwm.stop()
        self._reverse_pwm.stop()
        GPIO.cleanup()

    def update_max_speed(self, forward_delta, reverse_delta):
        self._max_forward_speed = self._squash(
            self._max_forward_speed + forward_delta)
        self._max_reverse_speed = self._squash(
            self._max_reverse_speed + reverse_delta)

    @staticmethod
    def _squash(val):
        return min(1.0, max(0.0, val))

    def _dutycycle(self, speed, max_speed=1.0):
        return (-speed * max_speed + 1) * 100.


class Buttons(object):
    def __init__(self, joystick):
        self._current = None
        self._previous = None
        self._joystick = joystick
        self._nbuttons = joystick.get_numbuttons()

    def update(self):
        self._previous = self._current
        self._current = tuple(self._joystick.get_button(b)
                              for b in xrange(self._nbuttons))

    def is_pressed(self, b):
        return self._current[b] and not self._previous[b]


def main():
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    pygame.display.init()

    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    buttons = Buttons(joystick)

    car = Car()

    print('Entering event loop, press CTRL+C to quit')
    try:
        while True:
            pygame.event.wait()
            _ = pygame.event.get()
            x = joystick.get_axis(2)
            y = joystick.get_axis(1)
            print('\rx={:.2f}, y={:.2f}'.format(x, y), end='')

            car.set_direction(x)
            car.set_speed(-y)

            buttons.update()
            forward_delta = .1 * (buttons.is_pressed(4) - buttons.is_pressed(6))
            reverse_delta = .1 * (buttons.is_pressed(5) - buttons.is_pressed(7))
            car.update_max_speed(forward_delta, reverse_delta)
    except KeyboardInterrupt:
        pass
    finally:
        car.shutdown()


if __name__ == '__main__':
    main()
