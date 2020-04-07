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


class _Actuator:
    """
    This is a base class for linear actuators that are controlled by a raspberry.Spout.
    """

    def __init__(self, pin, pin2=None):
        self._pin = pin
        self._pin2 = pin2

    def set_position(self, position):
        """
        Set the position of the actuators.
        """


class Actuonix_PG12_P(_Actuator):
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
        _Actuator.__init__(self, pin, pin2)
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


class Actuonix_L12_S(_Actuator):
    """
    Actuonix L12-S Linear Actuator (10mm stroke, 210:1 ratio, 12V)

    The step_time attribute is how many milliseconds of 12V input is required to move
    the actuator 1 mm.
    """

    _step_time = 0.200
    _duty_cycle = 20
    _frequency = 100

    def __init__(self, pin, pin2=None):
        _Actuator.__init__(self, pin, pin2)
        self._enabled = False
        self._position = 1

        GPIO.setup(pin, GPIO.OUT, initial=False)
        GPIO.setup(pin2, GPIO.OUT, initial=False)
        self._pwm = GPIO.PWM(pin, self._frequency)
        self._pwm2 = GPIO.PWM(pin2, self._frequency)
        self._pwm.start(0)
        self._pwm2.start(0)

        self.move(False, 1)
        self.move(True, 0.120)

    def set_position(self, position):
        step = position - self._position
        duration = abs(step * self._step_time)
        if step > 0:
            self._pwm.ChangeDutyCycle(self._duty_cycle)
            time.sleep(duration)
            self._pwm.ChangeDutyCycle(0)
        elif step < 0:
            self._pwm2.ChangeDutyCycle(self._duty_cycle)
            time.sleep(duration)
            self._pwm2.ChangeDutyCycle(0)
        self._position = position

    def move(self, retract, duration):
        """
        Freely move the actuators by a specified duration.

        Parameters
        ----------
        advance : :class:`bool`
            If True, actuators will retract, otherwise they will advance.

        duration : :class`float`
            Duration in seconds to apply power.

        """
        pwm = self._pwm if retract else self._pwm2
        pwm.ChangeDutyCycle(self._duty_cycle)
        time.sleep(duration)
        pwm.ChangeDutyCycle(0)

    def __del__(self):
        self._pwm.ChangeDutyCycle(0)
        self._pwm.stop()
        self._pwm2.ChangeDutyCycle(0)
        self._pwm2.stop()


class Spout:
    """
    This object represents and controls a single target spout, which controls a cue and
    a reward dispenser using GPIO outputs, listens to a touch sensor with a GPIO input,
    and controls one linear actuator.

    Parameters
    ----------
    pins : dict
        Dictionary containing pin numbers for cue, touch, reward and actuator.

    actuator : class, optional
        Class used to control the spout's linear actuator. By default, the
        Actuonix_L12_S is used.

    """

    def __init__(self, pins, actuator=None):
        self.cue_pin = pins["cue"]
        self.touch_pin = pins["touch"]
        self.reward_pin = pins["reward"]
        self.actuator_pin = pins["actuator"]
        self.actuator_reverse_pin = pins["actuator_reverse"]

        if actuator is None:
            actuator = Actuonix_PG12_P
        elif not isinstance(actuator, _Actuator):
            raise SystemError(f"Unknown actuator: {actuator}")
        self._actuator = actuator(self.actuator_pin, self.actuator_reverse_pin)

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
