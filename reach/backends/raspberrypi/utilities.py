"""
Raspberry Pi Utilities
======================

This subclass of :class`RaspberryPi` provides utilities that are helpful when setting up
and using a reach training box.

"""


import RPi.GPIO as GPIO
import time

from .raspberry import RaspberryPi


class UtilityPi(RaspberryPi):
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
                self.spouts[self._button_pins.index(pin)].reward,
                not GPIO.input(pin),
            )

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_toggle,
                bouncetime=20,
            )

    def test_sensors(self):
        """
        Print a message upon contact with any touch sensor.
        """
        print("Testing all touch sensors.")

        spout_pins = [i.touch for i in self.spouts]

        def _print_touch(pin):
            if pin == self.paw_pins[0]:
                print(f"Left:    {GPIO.input(pin)}")
            elif pin == self.paw_pins[1]:
                print(f"Right:   {GPIO.input(pin)}")
            else:
                print(f"Spout {spout_pins.index(pin) + 1}: {GPIO.input(pin)}")

        for pin in spout_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_print_touch,
                bouncetime=10,
            )

        for pin in self.paw_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_print_touch,
                bouncetime=10,
            )

    def toggle_spout_leds(self):
        """
        Toggle the two target spout LEDs with buttons 1 and 2.
        """
        print("Push button to toggle corresponding LED.")

        led_pins = [i.cue for i in self.spouts]

        def _toggle(pin):
            spout_number = self._button_pins.index(pin)
            state = GPIO.input(led_pins[spout_number])
            GPIO.output(led_pins[spout_number], not state)

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_toggle,
                bouncetime=500,
            )

    def test_reward_volume(self):
        """
        Measure volume of water dispensed by a specified duration.
        """
        self._reward_duration = float(input("Specify duration to dispense in ms: "))
        print("Press button 0 or 1 to dispense from corresponding spout.")

        def _dispense(pin):
            self.dispense_water(self._button_pins.index(pin))

        for pin in self._button_pins[0:2]:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_dispense,
                bouncetime=500,
            )

    def test_air_puffs(self):
        """
        Trigger air puffs upon press of button 0.
        """
        self._air_puff_duration = float(input("Specify duration to puff air in ms: "))
        print("Press button 0 to trigger air puff.")
        print("Press button 1 to open solenoids.")

        GPIO.add_event_detect(
            self._button_pins[0],
            GPIO.FALLING,
            callback=self.air_puff,
            bouncetime=500,
        )

        def _toggle(pin):
            time.sleep(0.010)
            for spout in self.spouts:
                GPIO.output(
                    spout.reward,
                    not GPIO.input(pin),
                )

        GPIO.add_event_detect(
            self._button_pins[1],
            GPIO.BOTH,
            callback=_toggle,
            bouncetime=20,
        )

    def test_reward_volume_with_air_puffs(self):
        """
        Trigger air puffs upon press of button 0 with specified water volume
        dispensed to both spouts upon press of button 1.
        """
        self._reward_duration = float(input("Specify duration to dispense in ms: "))
        self._air_puff_duration = float(input("Specify duration to puff air in ms: "))

        print("Press button 0 to trigger air puff.")
        print("Press button 1 to dispense water.")

        GPIO.add_event_detect(
            self._button_pins[0],
            GPIO.FALLING,
            callback=self.air_puff,
            bouncetime=500,
        )

        def _dispense(pin):
            time.sleep(0.010)
            for spout_number in [0, 1]:
                self.dispense_water(spout_number)

        GPIO.add_event_detect(
            self._button_pins[1],
            GPIO.FALLING,
            callback=_dispense,
            bouncetime=500,
        )

    def test_buttons(self):
        """
        When either button is pressed, print its number.
        """
        print("Press the buttons to print their corresponding numbers.")

        def _print_number(pin):
            if GPIO.input(pin):
                print(f'You released button: {self._button_pins.index(pin)}')
            else:
                print(f'You pressed button: {self._button_pins.index(pin)}')

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_print_number,
                bouncetime=500,
            )

    def step_actuators(self):
        """
        Move the actuator positions along steps using the buttons.
        """
        print("Press button 0 or 1 to step actuator forward or back.")
        print("Press button 2 or 3 to retract or advance actuator fully.")

        self.position_spouts(self.spout_position)

        def _move_spouts(pin):
            button_num = self._button_pins.index(pin)
            if button_num == 0:
                self.spout_position -= 1
            if button_num == 1:
                self.spout_position += 1
            if button_num == 2:
                self.spout_position = 1
            if button_num == 3:
                self.spout_position = 7
            print(f'Spout position: {self.spout_position}')
            self.position_spouts(self.spout_position)

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_move_spouts,
                bouncetime=1000,
            )
