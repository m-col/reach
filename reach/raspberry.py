"""
Raspberry Pis
=============

The :class:`._RPi` object represents a raspberry pi and directly controls GPIO
pins used to operate the training box hardware during behavioural training.

The :class:`._RPi_Mock` object represents the same as :class:`._RPi` except
never handles any hardware, acting as a mock raspberry pi.

If we try to create an instance of :class:`._RPi` but do not have access to the
RPi.GPIO library (and therefore are not working on a raspberry pi), an
:class:`._RPi_Mock` instance is returned instead.

"""


import signal
import time


_pin_numbers = {
    'start_button' : 4,
    'paw_sensors' : [17, 18],
    'spouts' : [
        {
            'cue': 5,
            'touch': 27,
            'solenoid': 25,
        },
        {
            'cue': 0,
            'touch': 0,
            'solenoid': 0,
        },
    ],
}


class _RPi:
    """
    An instance of a raspberry pi and its GPIO pins.

    Parameters
    ----------
    spout_count : :class:`int`
        The number of spouts to be used for the current training session.

    Attributes
    ----------
    _start_button_pin : :class:`int`
        The pin number that listens to the start button.

    _paw_pins : :class:`list` of 2 :class:`ints`
        The two pin numbers that listen to the two paw rests, in the form
        [left, right].

    _spouts : :class:`list` of :class:`dicts`
        List containing, for len(_spouts) spouts, dicts listing the pin numbers
        for each spout's cue, touch and solenoid pins.

    """

    def __init__(self, spout_count):
        """
        Initialise the pi and set initial pin states.
        """
        self._start_button_pin = _pin_numbers['start_button']
        self._paw_pins = _pin_numbers['paw_sensors']
        self._spouts = [
            _pin_numbers['spouts'][:self.spout_count]
        ]

        self._initialise_pins()

        signal.signal(
            signal.SIGINT,
            self._cleanup
        )

    @classmethod
    def _init_with_library_check(cls, spout_count):
        """
        Check for presence of RPI.GPIO library to determine whether we are
        working on a raspberry pi or another machine. In the case of the
        former, an instance of :class:`._RPi_Mock` is returned in place of
        :class:`._RPi`.

        Parameters
        ----------
        spout_count : :class:`int`
            The number of spouts to be used for the current training session.

        """
        try:
            import RPi.GPIO as GPIO
        except ModuleNotFoundError:
            print('RPi.GPIO not found. Continuing with mock raspberry pi.')
            return _RPi_Mock(spout_count)

        return cls(spout_count)

    def _initialise_pins(self):
        """
        Set initial state of pins.
        """

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(
            self._start_button_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP
        )

        GPIO.setup(
            self._paw_pins,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN
        )

        for spout in self._spouts:
            GPIO.setup(spout['cue'], GPIO.OUT, initial=False)
            GPIO.setup(spout['touch'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(spout['solenoid'], GPIO.OUT, initial=False)

            spout['cue_timepoints'] = []
            spout['touch_timepoints'] = []

    def _wait_to_start(self):
        """
        Block the program and wait until the 'start' button is pressed at the
        training box. Once this is pressed, the training session begins.
        """
        GPIO.wait_for_edge(
            self._start_button_pin,
            GPIO.FALLING
        )

    def _monitor_sensors(self, reset_iti, increase_spont_reaches):
        """
        Monitor touch during the inter-trial interval to execute callback
        functions upon movement events.

        Parameters
        ----------
        reset_iti : :class:`func`
            Callback function executed upon lift of either paw.

        increase_spont_reaches : :class:`func`
            Callback function executed upon contact with any spout touch
            sensors.

        """
        for paw in self._paw_pins:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=reset_iti,
                bouncetime=100
            )

        for spout in self._spouts:
            GPIO.add_event_detect(
                spout['touch'],
                GPIO.RISING,
                callback=increase_spont_reaches,
                bouncetime=100
            )

    def _set_button_callback(self, callback_function):
        """
        Add a callback function to be executed upon button press.

        Parameters
        ----------
        callback_function : :class:`func`
            Function to be executed upon button press.
            
        """
        GPIO.remove_event_detect(self._start_button_pin)
        GPIO.add_event_detect(
            self._start_button_pin,
            GPIO.FALLING,
            callback=callback_function,
            bouncetime=500
        )

    def _wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ", end='', flush=True)
        while not all([GPIO.input(self._paw_pins[0]),
                       GPIO.input(self._paw_pins[1])]):
            time.sleep(0.020)

    def _disable_sensors(self):
        """
        Remove event detection from all touch sensors at the end of the
        inter-trial interval.
        """
        for paw_pin in self._paw_pins:
            GPIO.remove_event_detect(paw_pin)
        for spout in self._spouts:
            GPIO.remove_event_detect(spout['touch'])

    def _start_trial(self, spout_number, reward_func, incorrect_func):
        """
        Illuminate a cue, record the time, and add callback functions to be
        executed upon grasp of target spouts during trial.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        reward_func : :class:`func`
            Callback function to be executed upon successful grasp of target
            spout.

        incorrect_func : :class:`func`
            Callback function to be executed upon incorrect grasp of non-target
            spout.

        """
        print("Cue illuminated")
        self._spouts[spout_number]['cue_timepoints'].append(time.time())
        GPIO.output(self._spouts[spout_number]['cue'], True)

        GPIO.add_event_detect(
            self._spouts[spout_number]['touch'],
            GPIO.RISING,
            callback=reward_func,
            bouncetime=1000
        )

        if len(spouts) > 1:
            GPIO.add_event_detect(
                self._spouts[1 - spout_number]['touch'],
                GPIO.RISING,
                callback=incorrect_func,
                bouncetime=1000
            )

    def _successful_grasp(self, spout_number):
        """
        Disable target spout LED and record time upon successful cued grasp of
        trial target spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        GPIO.output(self._spouts[spout_number]['cue'], False)
        self._spouts[spout_number]['touch_timepoints'].append(time.time())

    def _incorrect_grasp(self, spout_number):
        """
        Disable target spout LED and record time upon grasp of incorrect spout
        during trial.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        GPIO.output(self._spouts[spout_number]['cue'], False)
        self._spouts[1 - spout_number]['touch_timepoints'].append(time.time())

    def _dispense_water(self, spout_number, duration_ms):
        """
        Dispense water from a specified spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number to dispense water from.

        duration_ms : :class:`int`
            The duration in milliseconds to open the solenoid.

        """
        GPIO.output(self._spouts[spout_number]['solenoid'], True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self._spouts[spout_number]['solenoid'], False)

    def _end_trial(self):
        """
        Disable target spout LED and remove spout touch sensors event
        callbacks.
        """
        for spout in self._spouts:
            GPIO.output(spouts['cue'], False)
            GPIO.remove_event_detect(spout['touch'])

    def _cleanup(self, signal_number=0, frame=0):
        """
        Clean up and uninitialise pins.
        """
        for spout in self._spouts:
            GPIO.output(spout['solenoid'], False)
        GPIO.cleanup()


class _RPi_Mock(_RPi):
    """
    A mock instance of a raspberry pi and its GPIO pins. This class is a
    fallback for :class:`_.RPi` when the RPi.GPIO library cannot be loaded,
    which assumes that we are working on a non-raspberry pi machine.

    This subclass overrides most methods to replace all calls to RPi.GPIO to
    instead keep track of hypothetical pin state changes. 

    Attributes
    ----------
    _pin_states : :class:`list` of 27 :class:`int`s
        This stores the state of all 27 raspberry pi GPIO pins. This way, each
        pin can be indexed using the inherited pin number attributes to read or
        change state.

    """

    def _initialise_pins(self):
        """
        Set initial state of the mock pins.
        """
        self._pin_states = [0] * 27
        self._pin_states[self._start_button_pin] = 1

        for spout in self._spouts:
            spout['cue_t'] = []
            spout['touch_t'] = []

    def _wait_to_start(self):
        """
        Instead of blocking execution, simply print a message.
        """
        print('Mock start button pressed here')

    def _monitor_sensors(self, *args, **kwargs):
        """
        Pretend to listen to inter-trial events but instead do nothing.
        """
        pass

    def _set_button_callback(self, *args, **kwargs):
        """
        Pretend to add a callback function to be executed upon button press.
        """
        pass

    def _wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ", end='', flush=True)
        time.sleep(1)

    def _disable_sensors(self):
        """
        Pretend to remove event detection from all touch sensors at the end of
        the inter-trial interval.
        """
        pass

    def _start_trial(self, spout_number, *args, **kwargs):
        """
        Record the trial start time.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's hypothetical reach
            target.

        """
        print("Cue illuminated")
        self._spouts[spout_number]['cue_timepoints'].append(time.time())

    def _successful_grasp(self, spout_number):
        """
        Record the time upon successful cued grasp of hypothetical target
        spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        self._spouts[spout_number]['touch_timepoints'].append(time.time())

    def _incorrect_grasp(self, spout_number):
        """
        Record time upon grasp of fictional incorrect spout during mock trial.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        self._spouts[1 - spout_number]['touch_timepoints'].append(time.time())

    def _dispense_water(self, spout_number, duration_ms):
        """
        Pretend to dispense water from a specified spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number that would dispense water if this were real.

        duration_ms : :class:`int`
            The duration in milliseconds to wait pretending to dispense.

        """
        time.sleep(duration_ms / 1000)

    def _end_trial(self):
        """
        Pretend to disable target spout LED and remove spout touch sensors
        event callbacks.
        """
        pass

    def _cleanup(self):
        """
        Pretend to clean up and uninitialise pins.
        """
        pass
