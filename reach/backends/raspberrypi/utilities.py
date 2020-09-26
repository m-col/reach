"""
Raspberry Pi Utilities
======================

This subclass of :class`RaspberryPi` provides utilities that are helpful when setting up
and using a reach training box.

It requires the readchar library: https://github.com/magmax/python-readchar
"""

import RPi.GPIO as GPIO  # pylint: disable=import-error
import readchar

from reach.session import Targets
from reach.backends.raspberrypi.raspberry import RaspberryPi

UP_KEY = readchar.key.UP
DOWN_KEY = readchar.key.DOWN
RIGHT_KEY = readchar.key.RIGHT
LEFT_KEY = readchar.key.LEFT
EXIT = readchar.key.SPACE


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
            if pin in self._paw_pins:
                index = self._paw_pins.index(pin)
                print(f"Paw pin {index}:    {GPIO.input(pin)}")
            if pin in spout_pins:
                print(f"Spout {spout_pins.index(pin) + 1}: {GPIO.input(pin)}")

        for pin in spout_pins:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_print_touch, bouncetime=10,
            )

        for pin in self._paw_pins:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_print_touch, bouncetime=10,
            )

        input("Press enter key to stop.\n")

    def toggle_solenoids(self):
        """
        Open and close the water reward solenoids individually.
        """
        print("Press the left or right keys to open and close the corresponding solenoid.")
        print("Press space key to stop.")

        left_open = False
        right_open = False

        while True:
            key = readchar.readkey()
            if key == LEFT_KEY:
                left_open = not left_open
                GPIO.output(self.spouts[Targets.LEFT].reward_pin, left_open)
            elif key == RIGHT_KEY:
                right_open = not right_open
                GPIO.output(self.spouts[Targets.RIGHT].reward_pin, right_open)
            elif key == EXIT:
                break

    def toggle_spout_leds(self):
        """
        Toggle the two target spout LEDs.
        """
        print("Press the left or right keys to toggle the corresponding LED.")
        print("Press space key to stop.")

        left_on = False
        right_on = False

        while True:
            key = readchar.readkey()
            if key == LEFT_KEY:
                left_on = not left_on
                GPIO.output(self.spouts[Targets.LEFT].cue_pin, left_on)
            elif key == RIGHT_KEY:
                right_on = not right_on
                GPIO.output(self.spouts[Targets.RIGHT].cue_pin, right_on)
            elif key == EXIT:
                break

    def dispense_reward_volume(self):
        """
        Measure volume of water dispensed by a specified duration.
        """
        print("Press the left or right key to dispense a reward from the corresponding spout.")
        print("Press space key to stop.")

        while True:
            key = readchar.readkey()
            if key == LEFT_KEY:
                self.give_reward(Targets.LEFT)
            elif key == RIGHT_KEY:
                self.give_reward(Targets.RIGHT)
            elif key == EXIT:
                break

    def step_actuators(self):
        """
        Move the actuator positions along steps.
        """
        print("Press right or left key to step actuator back or foward.")
        print("Press up or down key to retract or advance actuator fully.")
        print("Press space key to stop.")

        spout_position = 1
        self.position_spouts(spout_position)

        while True:
            key = readchar.readkey()
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
            elif key == EXIT:
                break
            print(f"Spout position: {spout_position}")
            self.position_spouts(spout_position)
