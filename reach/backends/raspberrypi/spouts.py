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


import RPi.GPIO as GPIO
import time


class _Actuator:
    """
    This is a base class for linear actuators that are controlled by a raspberry.Spout.
    """
    def disable(self):
        pass

    def set_position(self):
        pass


class Actuonix_PG12_P(_Actuator):
    """
    Actuonix PQ12-P Linear Actuator (20mm stroke, 63:1 ratio, 6V)

    These duty cycles produce 1 mm intervals in position.
    """
    _DUTY_CYCLES = (
        7.5, 7.7, 7.95, 8.2, 8.4, 8.7, 8.9,
    )

    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT, initial=False)
        self._duty_cycle = 0
        self._pwm = GPIO.PWM(pin, 50)
        self._pin = pin
        self._enabled = False

    def _enable(self):
        self._pwm.start(self._duty_cycle)
        self._enabled = True

    def _set_duty_cycle(self, duty_cycle):
        """
        Set duty cycle of actuator PWM.
        """
        if not duty_cycle == 0:
            if duty_cycle > 9.5:
                duty_cycle = 9.5
            elif duty_cycle < 7.3:
                duty_cycle = 7.3

        self._duty_cycle = duty_cycle
        self._pwm.ChangeDutyCycle(duty_cycle)

    def disable(self):
        """
        Disable PWM.
        """
        if self._enabled:
            self._set_duty_cycle(0)
            self._pwm.stop()

    def set_position(self, position):
        """
        Move the actuator to a determined position.
        """
        if not self._enabled:
            self._enable()
        self._set_duty_cycle(Actuonix_PG12_P._DUTY_CYCLES[position - 1])


class Actuonix_L12_S(_Actuator):
    """
    Actuonix L12-S Linear Actuator (10mm stroke, 210:1 ratio, 12V)

    The step_time attribute is how many milliseconds of 12V input is required to move
    the actuator 1 mm.
    """
    step_time = 0.014

    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT, initial=False)
        self._pin = pin
        self._position = None

    def set_position(self, position):
        step = position - self._position
        self._set_polarity(step)
        GPIO.output(self._pin, True)
        time.sleep(Actuonix_L12_S.step_time)
        GPIO.output(self._pin, False)
        self._position = position

    def _set_polarity(self, direction):
        """
        This switches the direction that voltage is applied to the actuator to
        determine which direction it will move.

        Parameters
        ----------
        direction : int
            A positive value indicates retraction from mouse and increase of
            self._position, and a negative for advancement toward mouse.

        """
        pass


class Spout:
    """
    This object represents and controls a single target spout, which controls a cue and
    a reward dispenser using GPIO outputs, listens to a touch sensor with a GPIO input,
    and controls one linear actuator.

    Parameters
    ----------
    pins : dict
        Dictionary containing pin numbers for cue, touch, reward and actuator.

    actuator : class (optional)
        Class used to control the spout's linear actuator. By default, the
        Actuonix_L12_S is used.

    """
    def __init__(self, pins, actuator=None):
        self.cue_pin = pins['cue']
        self.touch_pin = pins['touch']
        self.reward_pin = pins['reward']
        self.actuator_pin = pins['actuator']

        if actuator is None:
            actuator = Actuonix_L12_S
        elif not isinstance(actuator, _Actuator):
            SystemError(f'Unknown actuator: {actuator}')
        self._actuator = actuator(self.actuator_pin)

        GPIO.setup(self.cue_pin, GPIO.OUT, initial=False)
        GPIO.setup(self.touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.reward_pin, GPIO.OUT, initial=False)

    def disable(self):
        """
        Disable actuator and close solenoid valve.
        """
        GPIO.output(self.reward_pin, False)
        self._actuator.disable()

    def set_position(self, position):
        """
        Set the position of the spout using the actuator.
        """
        self._actuator.set_position(position)
