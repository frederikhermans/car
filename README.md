# Control a toy RC car with a PS4 controller

Our oldest son has this [RC car](https://www.amazon.de/dp/B07G876251). Unfortunately, the remote controller broke on the first day. I've hooked up the car to a PS4 controller using a Raspberry Pi. Driving the car with the PS4 controller is much more fun than using the original controller ever was!

# Quick instructions

## Ingredients

You need

* A Raspberry Pi with a Bluetooth module
* A PS4 controller
* A remote controller capable of sending commands to the car
  * This may seem like a catch 22. However, our experience is that it is the button springs that are most likely to fail on the controller. Even if a button breaks, the radio components usually continue to work.

## Connecting the Pi to the (broken) controller

The controller's circuit board is very simple. I just soldered four jumper wires to the button outputs. The wires are then connected to the Pi's pins 4 (steer left button), 17 (steer right), 27 (forward), and 22 (reverse).

<!-- Here's what it looks like. I apologize for the poor soldering job.

![Controller circuit board with jumper wires](photos/controller.jpg?raw=true) -->

## Connecting the PS4 controller to the Pi

Power on Bluetooth

```
$ sudo bluetoothctl
[bluetooth]# power on
Changing power on succeeded
```

Next, follow these [excellent instructions](https://github.com/macunixs/dualshock4-pi) for installing and loading the PS4 drivers on the Raspberry Pi.

## Run the script

Run `$ sudo python -u car/car.py`. Drive your car! Woohoo!

It's a bit unfortunate that the script needs to be run as root. The issue is that it is built on pygame for accessing the PS4 controller, and pygame wants a video output. I'm using the framebuffer (fbcon), and I haven't yet figured out how to access it without root privileges.
