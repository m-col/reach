"""
Raspberry Pi Utilities
======================

This subclass of :class`RaspberryPi` provides utilities that are helpful when setting up
and using a reach training box.

"""


import time
import RPi.GPIO as GPIO  # pylint: disable=import-error

from .raspberry import RaspberryPi


class Utilities(RaspberryPi):
    """
    A representation of a Raspberry Pi that exposes utilities for testing the training
    hardware.
    """

    def __init__(self):
        RaspberryPi.__init__(self)
        self.spout_position = 1

    def hold_open_solenoid(self):
        """
        Hold open a target's solenoid continuous while a button is held.
        """
        print("Hold a button to open the corresponding solenoid.")

        def _toggle(pin):
            time.sleep(0.010)
            GPIO.output(
                self.spouts[self._button_pins.index(pin)].reward_pin,
                not GPIO.input(pin),
            )

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_toggle, bouncetime=20,
            )

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

    def toggle_spout_leds(self):
        """
        Toggle the two target spout LEDs with buttons 1 and 2.
        """
        print("Push button to toggle corresponding LED.")

        led_pins = [i.cue_pin for i in self.spouts]

        def _toggle(pin):
            spout_number = self._button_pins.index(pin)
            state = GPIO.input(led_pins[spout_number])
            GPIO.output(led_pins[spout_number], not state)

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, callback=_toggle, bouncetime=500,
            )

    def test_reward_volume(self):
        """
        Measure volume of water dispensed by a specified duration.
        """
        self._reward_duration = float(input("Specify duration to dispense in s: "))
        print("Press button 0 or 1 to dispense from corresponding spout.")

        def _dispense(pin):
            self.give_reward(self._button_pins.index(pin))

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, callback=_dispense, bouncetime=500,
            )

    def step_actuators(self):
        """
        Move the actuator positions along steps using the buttons.
        """
        print("Press button 0 or 1 to step actuator back or foward.")
        print("Press button 2 or 3 to retract or advance actuator fully.")

        self.position_spouts(self.spout_position)

        def _move_spouts(pin):
            button_num = self._button_pins.index(pin)
            if button_num == 0:
                self.spout_position -= 1
            if button_num == 1:
                self.spout_position += 1
            if button_num == 2 or self.spout_position < 1:
                self.spout_position = 1
            if button_num == 3 or self.spout_position > 7:
                self.spout_position = 7
            print(f"Spout position: {self.spout_position}")
            self.position_spouts(self.spout_position)

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, callback=_move_spouts, bouncetime=1000,
            )

    def move_actuators(self):
        """
        Freely move the actuator positions.
        """
        duration = float(input("Specify duration in seconds to apply power: "))
        print("Press button 0 or 1 to move actuators forward or back.")

        def _move_spouts(pin):
            button_num = self._button_pins.index(pin)
            for spout in self.spouts:
                spout.move(button_num, duration)

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin, GPIO.FALLING, callback=_move_spouts, bouncetime=200,
            )
