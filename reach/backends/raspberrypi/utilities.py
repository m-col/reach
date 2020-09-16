"""
Raspberry Pi Utilities
======================

This subclass of :class`RaspberryPi` provides utilities that are helpful when setting up
and using a reach training box.

It requires the readchar library: https://github.com/magmax/python-readchar
"""


import time
import RPi.GPIO as GPIO  # pylint: disable=import-error
from readchar import readchar

from .raspberry import RaspberryPi

UP_KEY = '\x1b[A'
DOWN_KEY = '\x1b[B'
RIGHT_KEY = '\x1b[C'
LEFT_KEY = '\x1b[D'


class Utilities(RaspberryPi):
    """
    A representation of a Raspberry Pi that exposes utilities for testing the training
    hardware.
    """
    def test_sensors(self):
        """
        Print a message upon contact with any touch sensor.
        """
        print("Testing all touch sensors.")

        spout_pins = [i.touch_pin for i in self.spouts]

        def _print_touch(pin):
            if pin == self._paw_pins[0]:
                print(f"Left:    {GPIO.input(pin)}")
            elif pin == self._paw_pins[1]:
                print(f"Right:   {GPIO.input(pin)}")
            else:
                print(f"Spout {spout_pins.index(pin) + 1}: {GPIO.input(pin)}")

        for pin in spout_pins:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_print_touch, bouncetime=10,
            )

        for pin in self._paw_pins:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_print_touch, bouncetime=10,
            )

    def toggle_solenoid(self):
        """
        Open and close the water reward solenoids individually.
        """
        print("Press the left or right keys to open and close the corresponding solenoid.")

        left_open = False
        right_open = False

        while True:
            key = readchar()
            if key == LEFT_KEY:
                GPIO.output(self.spouts[0].reward_pin, not left_open)
            elif key == RIGHT_KEY:
                GPIO.output(self.spouts[1].reward_pin, not right_open)
            else:
                break

    def toggle_spout_leds(self):
        """
        Toggle the two target spout LEDs.
        """
        print("Press the left or right keys to toggle the corresponding LED.")

        left_on = False
        right_on = False

        while True:
            key = readchar()
            if key == LEFT_KEY:
                GPIO.output(self.spouts[0].cue_pin, not left_on)
            elif key == RIGHT_KEY:
                GPIO.output(self.spouts[1].cue_pin, not right_on)
            else:
                break

    def test_reward_volume(self):
        """
        Measure volume of water dispensed by a specified duration.
        """
        print("Press the left or right key to dispense a reward from the corresponding spout.")

        while True:
            key = readchar()
            if key == LEFT_KEY:
                self.give_reward(0)
            elif key == RIGHT_KEY:
                self.give_reward(1)
            else:
                break

    def step_actuators(self):
        """
        Move the actuator positions along steps.
        """
        print("Press right or left key to step actuator back or foward.")
        print("Press up or down key to retract or advance actuator fully.")

        spout_position = 1
        self.position_spouts(spout_position)

        while True:
            key = readchar()
            if key == LEFT_KEY:
                if spout_position > 1:
                    spout_position -= 1
            elif key == RIGHT_KEY:
                if spout_position < 7:
                    spout_position += 1
            elif key == DOWN_KEY:
                spout_position = 1
            elif key == UP_KEY:
                spout_position = 7
            else:
                break
            print(f"Spout position: {spout_position}")
            self.position_spouts(spout_position)
