"""
Spouts and associated paraphernalia
===================================

This module contains the :class:`Spout` class, as well as other classes that are
controlled by spout instances in a one-to-one relationship. E.g. Each spout controls one
linear actuator, though different actuators can be specified for use during the task.

For future reference: the actuator and spout classes are not unified so that in the
future different cue, reward and touch sensor classes can be implemented and all handled
under one Spout class.

"""


import threading
import time
import RPi.GPIO as GPIO  # pylint: disable=import-error


class Actuonix_PG12_P:
    """
    Actuonix PQ12-P Linear Actuator (20mm stroke, 63:1 ratio, 6V)

    These duty cycles produce 1 mm intervals in position.
    """

    _DUTY_CYCLES = (
        7.2,
        7.7,
        7.95,
        8.2,
        8.4,
        8.7,
        8.9,
    )

    def __init__(self, pin, pin2=None):
        self._pin = pin
        self._pin2 = pin2
        GPIO.setup(pin, GPIO.OUT, initial=False)
        self._pwm = GPIO.PWM(pin, 50)
        self._duty_cycle = 0
        self._pwm.start(self._duty_cycle)
        self._disable_thread = None

    def set_position(self, position):
        """
        Move the actuator to a determined position.
        """
        duty_cycle = Actuonix_PG12_P._DUTY_CYCLES[position - 1]
        if not duty_cycle == 0:
            if duty_cycle > 9.5:
                duty_cycle = 9.5
            elif duty_cycle < 7.2:
                duty_cycle = 7.2

        if self._disable_thread and self._disable_thread.isAlive():
            time.sleep(1)
        self._pwm.ChangeDutyCycle(duty_cycle)
        self._duty_cycle = duty_cycle
        # wait a second and remove power in background
        self._disable_thread = threading.Thread(target=self._disable)
        self._disable_thread.start()

    def _disable(self):
        time.sleep(1)
        self._pwm.ChangeDutyCycle(0)


class Spout:
    """
    This object represents and controls a single target spout, which controls a cue and
    a reward dispenser using GPIO outputs, listens to a touch sensor with a GPIO input,
    and controls one linear actuator.

    Parameters
    ----------
    pins : dict
        Dictionary containing pin numbers for cue, touch, reward and actuator.

    """

    def __init__(self, pins):
        self.cue_pin = pins["cue"]
        self.touch_pin = pins["touch"]
        self.reward_pin = pins["reward"]
        self.actuator_pin = pins["actuator"]

        self._actuator = Actuonix_PG12_P(self.actuator_pin)
        GPIO.setup(self.cue_pin, GPIO.OUT, initial=False)
        GPIO.setup(self.touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.reward_pin, GPIO.OUT, initial=False)

    def cleanup(self):
        """
        Close solenoid valve.
        """
        GPIO.output(self.reward_pin, False)

    def set_position(self, position):
        """
        Set the position of the spout using the actuator.
        """
        self._actuator.set_position(position)

    def __getattr__(self, attr):
        """
        Forward any unfound attributes to the actuators.
        """
        if hasattr(self._actuator, attr):
            return getattr(self._actuator, attr)
        raise AttributeError
