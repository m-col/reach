"""
Raspberry Pis
=============

The :class:`RaspberryPi` class represents a raspberry pi and directly controls GPIO pins
used to operate the training box hardware during behavioural training.

"""


import RPi.GPIO as GPIO
import time

from .. import Backend
from . import spouts


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class RaspberryPi(Backend):
    """
    An instance of a raspberry pi and its GPIO pins.

    Parameters
    ---------
    actuator : :class:`class` (optional)
        An instance of reach.backends.raspberrypi.spouts._Actuator or a subclass. By
        default, reach.backends.raspberrypi.spouts.Actuonix_L12_S will be used.

    reward_duration : :class:`float` (optional)
        The duration in seconds for which the solenoid valves will be opened when
        dispensing water rewards. Default: 0.100 seconds.

    air_puff_duration : :class:`float` (optional)
        The duration in seconds for which the air puffs will be delivered. Default:
        0.030 seconds.

    button_bouncetime : :class:`float` (optional)
        The bouncetime in seconds assigned to the buttons to prevent accidental
        double-pressing. Default: 0.100

    """
    _PIN_NUMBERS = {
        'buttons': (2, 3, 4, 7),
        'paw_sensors': (5, 6),
        'air_puff': 18,
        'spouts': (
            {
                'cue': 23,
                'touch': 14,
                'reward': 16,
                'actuator': 12,
            },
            {
                'cue': 22,
                'touch': 15,
                'reward': 21,
                'actuator': 13,
            },
        ),
    }

    def __init__(
        self,
        actuator=None,
        reward_duration=None,
        air_puff_duration=None,
        button_bouncetime=None,
    ):
        Backend.__init__(self)
        self._reward_duration = reward_duration or 0.100
        self._air_puff_duration = air_puff_duration or 0.030
        self._button_bouncetime = (button_bouncetime or 0.100) * 1000

        self._button_pins = RaspberryPi._PIN_NUMBERS['buttons']
        self.paw_pins = RaspberryPi._PIN_NUMBERS['paw_sensors']
        self._air_puff = RaspberryPi._PIN_NUMBERS['air_puff']

        GPIO.setup(
            self._button_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP
        )
        GPIO.setup(
            self.paw_pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN
        )
        GPIO.setup(
            self._air_puff, GPIO.OUT, initial=False
        )

        self.spouts = [
            spouts.Spout(RaspberryPi._PIN_NUMBERS['spouts'][0], actuator),
            spouts.Spout(RaspberryPi._PIN_NUMBERS['spouts'][1], actuator),
        ]
        self.on_button = []

    def configure_callbacks(self, session):
        """
        Configure callback functions from Session.
        """
        self.on_iti_lift = _gpio_callback(session.on_iti_lift)
        self.on_iti_grasp = _gpio_callback(session.on_iti_grasp)
        self.on_trial_lift = _gpio_callback(session.on_trial_lift)
        self.on_trial_correct = _gpio_callback(session.on_trial_correct)
        self.on_trial_incorrect = _gpio_callback(session.on_trial_incorrect)
        self.on_button.append(_gpio_callback(session.reverse_shaping))
        self.on_button.append(_gpio_callback(session.extend_trial))

    def wait_to_start(self):
        """
        Block the program and wait until the enter key is hit. Once this is pressed, the
        training session begins.
        """
        input("Press enter to begin.\n")

    def disable_spouts(self):
        """
        Sets duty cycle of actuators to 0 to hold them stationary.
        """
        for spout in self.spouts:
            spout.disable()

    def position_spouts(self, position, spout_number=None):
        """
        Move one or both spouts to specified position.         """
        if position < 1:
            position = 1
        elif position > 7:
            position = 7

        for spout in self.spouts:
            spout.set_position(position)

    def advance_spouts(self, spout_number=None):
        if self._spout_position < 7:
            self._spout_position += 1
        self.position_spout(self._spout_position, spout_number)

    def retract_spouts(self, spout_number=None):
        if self._spout_position > 1:
            self._spout_position -= 1
        self.position_spout(self._spout_position, spout_number)

    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ")
        try:
            while not all([
                GPIO.input(self.paw_pins[0]),
                GPIO.input(self.paw_pins[1]),
            ]):
                time.sleep(0.010)
        except RuntimeError:
            # Ignore GPIO error when Ctrl-C cancels training
            pass

    def start_iti(self):
        """
        Assign callback functions to touch sensors and buttons.
        """
        self._disable_callbacks()

        for paw in self.paw_pins:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=self.on_iti_lift,
                bouncetime=100,
            )

        for spout in self.spouts:
            GPIO.add_event_detect(
                spout.touch_pin,
                GPIO.RISING,
                callback=self.on_iti_grasp,
                bouncetime=100,
            )

        for index, on_button in enumerate(self.on_button):
            GPIO.remove_event_detect(self._button_pins[index])
            GPIO.add_event_detect(
                self._button_pins[index],
                GPIO.FALLING,
                callback=on_button,
                bouncetime=self._button_bouncetime,
            )

    def start_trial(self, spout_number):
        """
        Illuminate a cue, record the time, and add callback functions to be executed
        upon grasp of target spouts during trial.
        """
        self._disable_callbacks()
        print("Cue illuminated")
        GPIO.output(self.spouts[spout_number].cue_pin, True)

        for paw_pin in self.paw_pins:
            GPIO.add_event_detect(
                paw_pin,
                GPIO.FALLING,
                callback=self.on_trial_lift,
                bouncetime=1000,
            )

        GPIO.add_event_detect(
            self.spouts[spout_number].touch_pin,
            GPIO.RISING,
            callback=self.on_trial_correct,
            bouncetime=1000,
        )

        GPIO.add_event_detect(
            self.spouts[1 - spout_number].touch_pin,
            GPIO.RISING,
            callback=self.on_trial_incorrect,
            bouncetime=1000,
        )

    def _disable_callbacks(self):
        """
        Remove event detection from all touch sensors at the end of the inter-trial
        interval.
        """
        for pin in self.paw_pins:
            GPIO.remove_event_detect(pin)

        for pin in self._button_pins:
            GPIO.remove_event_detect(pin)

        for spout in self.spouts:
            GPIO.remove_event_detect(spout.touch_pin)

    def dispense_water(self, spout_number):
        """
        Dispense water from a specified spout.
        """
        GPIO.output(self.spouts[spout_number].reward, True)
        time.sleep(self._reward_duration)
        GPIO.output(self.spouts[spout_number].reward, False)

    def miss_trial(self):
        """
        Trigger air puff to remove non-collected water at the end of a missed trial.
        """
        self.air_puff()

    def air_puff(self):
        """
        Trigger an air puff.
        """
        GPIO.output(self._air_puff, True)
        time.sleep(self._air_puff_duration)
        GPIO.output(self._air_puff, False)

    def end_trial(self):
        """
        Disable target spout LED and remove spout touch sensors event callbacks.
        """
        self._disable_callbacks()
        for spout in self.spouts:
            GPIO.output(spout.cue, False)

    def cleanup(self):
        """
        Clean up and uninitialise pins.
        """
        for spout in self.spouts:
            spout.disable()
        GPIO.cleanup()


def _gpio_callback(self, func):
    """
    Wraps a function so that it can be cleanly called as a RPi.GPIO event callback.
    """
    def _func(pin):
        return func()
    return _func
