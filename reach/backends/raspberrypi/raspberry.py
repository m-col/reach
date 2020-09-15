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
    reward_duration : :class:`float`, optional
        The duration in seconds for which the solenoid valves will be opened when
        dispensing water rewards. Default: 0.100 seconds.

    pin_numbers : :class:`dict`, optional
        A dictionary mapping raspberry pi GPIO pin numbers to components. This should be
        formatted exactly as :class:`RaspberryPi._PIN_NUMBERS`, with only the pin values
        changed.

    """

    _PIN_NUMBERS = {
        "paw_sensors": (5, 6),
        "spouts": (
            {
                "cue": 23,
                "touch": 14,
                "reward": 16,
                "actuator": 12,
            },
            {
                "cue": 22,
                "touch": 15,
                "reward": 21,
                "actuator": 13,
            },
        ),
    }

    def __init__(
        self,
        reward_duration=None,
        pin_numbers=None,
    ):
        Backend.__init__(self)
        self._reward_duration = reward_duration or 0.100

        if pin_numbers is None:
            pin_numbers = RaspberryPi._PIN_NUMBERS

        self._paw_pins = pin_numbers.get('paw_sensors', None)
        if self._paw_pins:
            GPIO.setup(self._paw_pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self._target_pins = [x["touch"] for x in pin_numbers["spouts"]]
        self.spouts = [
            spouts.Spout(pin_numbers["spouts"][0]),
            spouts.Spout(pin_numbers["spouts"][1]),
        ]

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

        if self._paw_pins:
            for paw in self._paw_pins:
                GPIO.add_event_detect(
                    paw, GPIO.FALLING, callback=self._paw_callback, bouncetime=250,
                )

        for spout in self.spouts:
            GPIO.add_event_detect(
                spout.touch_pin,
                GPIO.RISING,
                callback=self._spout_callback,
                bouncetime=100,
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
                self.session.on_trial_correct()
            else:
                self.session.on_trial_incorrect()
        else:
            self.session.on_iti_grasp(spout)

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
            while not all([GPIO.input(pin) for pin in self._paw_pins]):
                time.sleep(0.010)
        except RuntimeError:
            # Ignore GPIO error when Ctrl-C cancels training
            pass

    def start_trial(self, spout_number):
        """
        Change state to trial.
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

    def end_trial(self):
        """
        Disable target spout LEDs.
        """
        self._is_trial = False
        for spout in self.spouts:
            GPIO.output(spout.cue_pin, False)

    def cleanup(self):
        """
        Clean up, remove event callbacks and uninitialise pins.
        """
        if self._paw_pins:
            for pin in self._paw_pins:
                GPIO.remove_event_detect(pin)

        for spout in self.spouts:
            spout.cleanup()
            GPIO.remove_event_detect(spout.touch_pin)

    def __del__(self):
        """
        Cleanup only upon garbage-collection to prevent GPIO mode runtime errors in the
        event that callback functions still operate on GPIO pins after self.cleanup
        (though ideally this should never happen).
        """
        GPIO.cleanup()
