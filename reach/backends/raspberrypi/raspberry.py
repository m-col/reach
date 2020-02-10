"""
Raspberry Pis
=============

The :class:`RaspberryPi` class represents a raspberry pi and directly controls GPIO pins
used to operate the training box hardware during behavioural training.

"""


import time
import RPi.GPIO as GPIO  # pylint: disable=import-error

from .. import Backend
from . import spouts


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class RaspberryPi(Backend):
    """
    An instance of a raspberry pi and its GPIO pins.

    Parameters
    ---------
    actuator : :class:`class`, optional
        An instance of reach.backends.raspberrypi.spouts._Actuator or a subclass. By
        default, reach.backends.raspberrypi.spouts.Actuonix_L12_S will be used.

    reward_duration : :class:`float`, optional
        The duration in seconds for which the solenoid valves will be opened when
        dispensing water rewards. Default: 0.100 seconds.

    air_puff_duration : :class:`float`, optional
        The duration in seconds for which the air puffs will be delivered. Default:
        0.030 seconds.

    button_bouncetime : :class:`float`, optional
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
                'actuator_reverse': 19,
            },
            {
                'cue': 22,
                'touch': 15,
                'reward': 21,
                'actuator': 13,
                'actuator_reverse': 25,
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
        self._button_bouncetime = int((button_bouncetime or 0.100) * 1000)

        self._button_pins = RaspberryPi._PIN_NUMBERS['buttons']
        self._paw_pins = RaspberryPi._PIN_NUMBERS['paw_sensors']
        self._air_puff = RaspberryPi._PIN_NUMBERS['air_puff']
        self._target_pins = [x['touch'] for x in RaspberryPi._PIN_NUMBERS['spouts']]

        GPIO.setup(self._button_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._paw_pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self._air_puff, GPIO.OUT, initial=False)

        self.spouts = [
            spouts.Spout(RaspberryPi._PIN_NUMBERS['spouts'][0], actuator),
            spouts.Spout(RaspberryPi._PIN_NUMBERS['spouts'][1], actuator),
        ]
        self.on_button = []

        self._is_trial = False
        self._current_target_spout = 0
        self.session = None

    def configure_callbacks(self, session):
        """
        Store session to later get session methods that will be executed in GPIO
        callback functions.
        """
        self.session = session

    def wait_to_start(self):
        """
        Block the program and wait until the enter key is hit. Once this is pressed, the
        training session begins.
        """
        input("Press enter to begin.\n")

        for paw in self._paw_pins:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=self._paw_callback,
                bouncetime=250,
            )

        for spout in self.spouts:
            GPIO.add_event_detect(
                spout.touch_pin,
                GPIO.RISING,
                callback=self._spout_callback,
                bouncetime=100,
            )

        for button in self._button_pins:
            GPIO.add_event_detect(
                button,
                GPIO.FALLING,
                callback=self._button_callback,
                bouncetime=self._button_bouncetime,
            )

    def _paw_callback(self, pin):
        """
        Callback function assigned to paw sesnsors by GPIO.add_event_detect.
        """
        paw = self._paw_pins.index(pin)
        if self._is_trial:
            self.session.on_trial_lift(paw)
        else:
            self.session.on_iti_lift(paw)

    def _spout_callback(self, pin):
        """
        Callback function assigned to spout sensors by GPIO.add_event_detect.
        """
        spout = 0 if pin == self.spouts[0].touch_pin else 1
        if self._is_trial:
            if self._current_target_spout == spout:
                self.session.on_trial_correct(spout)
            else:
                self.session.on_trial_incorrect(spout)
        else:
            self.session.on_iti_grasp(spout)

    def _button_callback(self, pin):
        """
        Callback function assigned to buttons by GPIO.add_event_detect.
        """
        button = self._button_pins.index(pin)
        if button == 1:
            session.reverse_shaping()
        elif button == 2:
            session.extend_trial()

    def disable_spouts(self):
        """
        Disable the spouts from movement, if they support it.
        """
        for spout in self.spouts:
            spout.disable()

    def position_spouts(self, position, spout_number=None):
        """
        Move one or both spouts to specified position.
        """
        if position < 1:
            position = 1
        elif position > 7:
            position = 7

        for spout in self.spouts:
            spout.set_position(position)

    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ")
        try:
            while not all([
                GPIO.input(self._paw_pins[0]),
                GPIO.input(self._paw_pins[1]),
            ]):
                time.sleep(0.010)
        except RuntimeError:
            # Ignore GPIO error when Ctrl-C cancels training
            pass

    def start_iti(self):
        """
        Assign callback functions to touch sensors and buttons.
        """
        self._is_trial = False

    def start_trial(self, spout_number):
        """
        Illuminate a cue, record the time, and add callback functions to be executed
        upon grasp of target spouts during trial.
        """
        self._is_trial = True
        GPIO.output(self.spouts[spout_number].cue_pin, True)
        self._current_target_spout = spout_number
        print("Cue illuminated")

    def dispense_water(self, spout_number):
        """
        Dispense water from a specified spout.
        """
        GPIO.output(self.spouts[spout_number].reward_pin, True)
        time.sleep(self._reward_duration)
        GPIO.output(self.spouts[spout_number].reward_pin, False)

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
        for spout in self.spouts:
            GPIO.output(spout.cue_pin, False)

    def cleanup(self):
        """
        Clean up and uninitialise pins.
        """
        for pin in self._paw_pins:
            GPIO.remove_event_detect(pin)

        for pin in self._button_pins:
            GPIO.remove_event_detect(pin)

        for spout in self.spouts:
            spout.disable()
            GPIO.remove_event_detect(spout.touch_pin)

        GPIO.cleanup()
