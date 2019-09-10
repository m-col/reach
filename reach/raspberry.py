"""
Raspberry Pis
=============

The :class:`._RPiReal` object represents a raspberry pi and directly controls
GPIO pins used to operate the training box hardware during behavioural
training.

The :class:`._RPiMock` object represents the same as :class:`._RPi` except
never handles any hardware, acting as a mock raspberry pi.

Upon import of this module, we check if we can import RPI.GPIO. If we can, we
export :class:`._RPi` as :class:`._RPiReal`, else as :class:`._RPiMock`.

"""


import signal
import time

_IS_RASPBERRY_PI = True
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    _IS_RASPBERRY_PI = False


_PIN_NUMBERS = {
    'buttons': [4, 0],
    'paw_sensors': [17, 18],
    'spouts': [
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


class _RPiReal:
    """
    An instance of a raspberry pi and its GPIO pins.

    Parameters
    ----------
    spout_count : :class:`int`
        The number of spouts to be used for the current training session.

    Attributes
    ----------
    _button_pins : :class:`list` of 2 :class:`int`
        The pin numbers that listen to the left and right buttons.

    paw_pins : :class:`list` of 2 :class:`ints`
        The pin numbers that listen to the left and right paw rests.

    spouts : :class:`list` of :class:`dicts`
        List containing, for len(spouts) spouts, dicts listing the pin numbers
        for each spout's cue, touch and solenoid pins.

    """

    def __init__(self, spout_count):
        """
        Initialise the pi and set initial pin states.

        Parameters
        ----------
        spout_count : :class:`int`
            The number of spouts to be used for the current training session.

        """
        self._button_pins = _PIN_NUMBERS['buttons']
        self.paw_pins = _PIN_NUMBERS['paw_sensors']
        self.spouts = _PIN_NUMBERS['spouts'][:spout_count]

        self.initialise_pins()

        signal.signal(
            signal.SIGINT,
            self.cleanup
        )

    def initialise_pins(self):
        """
        Set initial state of pins.
        """

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(
            self._button_pins,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP
        )

        GPIO.setup(
            self.paw_pins,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN
        )

        for spout in self.spouts:
            GPIO.setup(spout['cue'], GPIO.OUT, initial=False)
            GPIO.setup(spout['touch'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(spout['solenoid'], GPIO.OUT, initial=False)
            spout['cue_timepoints'] = []
            spout['touch_timepoints'] = []

    def wait_to_start(self):
        """
        Block the program and wait until the left hand button is pressed at the
        training box. Once this is pressed, the training session begins.
        """
        print("Hit the left button to begin.")
        GPIO.wait_for_edge(
            self._button_pins[0],
            GPIO.FALLING
        )

    def monitor_sensors(self, reset_iti, increase_spont_reaches):
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
        for paw in self.paw_pins:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=reset_iti,
                bouncetime=100
            )

        for spout in self.spouts:
            GPIO.add_event_detect(
                spout['touch'],
                GPIO.RISING,
                callback=increase_spont_reaches,
                bouncetime=100
            )

    def set_button_callback(self, button, func):
        """
        Add a callback function to be executed upon button press.

        Parameters
        ----------
        button : :class:`int`
            The index of the button to assign the function to.

        callback_function : :class:`func`
            Function to be executed upon button press.

        """
        GPIO.remove_event_detect(self._button_pins[button])
        GPIO.add_event_detect(
            self._button_pins[button],
            GPIO.FALLING,
            callback=func,
            bouncetime=500
        )

    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print(
            "Waiting for rest... ",
            end="",
            flush=True
        )
        while not all([GPIO.input(self.paw_pins[0]),
                       GPIO.input(self.paw_pins[1])]):
            time.sleep(0.020)

    def disable_sensors(self):
        """
        Remove event detection from all touch sensors at the end of the
        inter-trial interval.
        """
        for paw_pin in self.paw_pins:
            GPIO.remove_event_detect(paw_pin)
        for spout in self.spouts:
            GPIO.remove_event_detect(spout['touch'])

    def start_trial(self, spout_number, reward_func, incorrect_func):
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
        self.spouts[spout_number]['cue_timepoints'].append(time.time())
        GPIO.output(self.spouts[spout_number]['cue'], True)

        GPIO.add_event_detect(
            self.spouts[spout_number]['touch'],
            GPIO.RISING,
            callback=reward_func,
            bouncetime=1000
        )

        if len(self.spouts) > 1:
            GPIO.add_event_detect(
                self.spouts[1 - spout_number]['touch'],
                GPIO.RISING,
                callback=incorrect_func,
                bouncetime=1000
            )

    def successful_grasp(self, spout_number):
        """
        Disable target spout LED and record time upon successful cued grasp of
        trial target spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        GPIO.output(self.spouts[spout_number]['cue'], False)
        self.spouts[spout_number]['touch_timepoints'].append(time.time())

    def incorrect_grasp(self, spout_number):
        """
        Disable target spout LED and record time upon grasp of incorrect spout
        during trial.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        GPIO.output(self.spouts[spout_number]['cue'], False)
        self.spouts[1 - spout_number]['touch_timepoints'].append(time.time())

    def dispense_water(self, spout_number, duration_ms):
        """
        Dispense water from a specified spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number to dispense water from i.e. 0=left, 1=right.

        duration_ms : :class:`int`
            The duration in milliseconds to open the solenoid.

        """
        GPIO.output(self.spouts[spout_number]['solenoid'], True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self.spouts[spout_number]['solenoid'], False)

    def end_trial(self):
        """
        Disable target spout LED and remove spout touch sensors event
        callbacks.
        """
        for spout in self.spouts:
            GPIO.output(spout['cue'], False)
            GPIO.remove_event_detect(spout['touch'])

    def cleanup(self, signal_number=0, frame=0):
        """
        Clean up and uninitialise pins.

        Parameters
        ----------
        signal_number : :class:`int`, optional
            Passed automatically by signal.signal.

        frame : :class:`int`, optional
            Passed automatically by signal.signal.

        """
        for spout in self.spouts:
            GPIO.output(spout['solenoid'], False)
        GPIO.cleanup()


class _RPiMock(_RPiReal):
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

    def initialise_pins(self):
        """
        Set initial state of the mock pins.
        """
        self._pin_states = [0] * 27
        for button in self._button_pins:
            self._pin_states[button] = 1 

        for spout in self.spouts:
            spout['cue_timepoints'] = []
            spout['touch_timepoints'] = []

    def wait_to_start(self):
        """
        Instead of blocking execution, simply print a message.
        """
        print("Hit the start button to begin.")

    def monitor_sensors(self, *args, **kwargs):
        """
        Pretend to listen to inter-trial events but instead do nothing.
        """

    def set_button_callback(self, *args, **kwargs):
        """
        Pretend to add a callback function to be executed upon button press.
        """

    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ", end='', flush=True)
        time.sleep(1)

    def disable_sensors(self):
        """
        Pretend to remove event detection from all touch sensors at the end of
        the inter-trial interval.
        """

    def start_trial(self, spout_number, *args, **kwargs):
        """
        Record the trial start time.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's hypothetical reach
            target.

        """
        print("Cue illuminated")
        self.spouts[spout_number]['cue_timepoints'].append(time.time())

    def successful_grasp(self, spout_number):
        """
        Record the time upon successful cued grasp of hypothetical target
        spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        self.spouts[spout_number]['touch_timepoints'].append(time.time())

    def incorrect_grasp(self, spout_number):
        """
        Record time upon grasp of fictional incorrect spout during mock trial.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        self.spouts[1 - spout_number]['touch_timepoints'].append(time.time())

    def dispense_water(self, spout_number, duration_ms):
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

    def end_trial(self):
        """
        Pretend to disable target spout LED and remove spout touch sensors
        event callbacks.
        """

    def cleanup(self):
        """
        Pretend to clean up and uninitialise pins.
        """


_RPi = _RPiReal if _IS_RASPBERRY_PI else _RPiMock


class UtilityPi(_RPiReal):
    """
    A subclass of :class:`_.RPi` that exposes some additional methods that
    serve as utilities for testing the training hardware.

    """

    def __init__(self):
        """
        This subclass interacts with both spouts so does not need the
        spout_count parameter that is passed to :class:`_RPi`.
        """
        self._button_pins = _PIN_NUMBERS['buttons']
        self.paw_pins = _PIN_NUMBERS['paw_sensors']
        self.spouts = _PIN_NUMBERS['spouts']

        self.initialise_pins()

        signal.signal(
            signal.SIGINT,
            self.cleanup
        )

    def hold_open_solenoid(self):
        """
        Hold open a solenoid to continuous while one of the two buttons is
        held.
        """
        print("Hold a button to open the corresponding solenoid.")

        def _toggle(pin):
            sleep(0.010)
            GPIO.output(
                self.spouts[self._button_pins.index(pin)]['solenoid'],
                not GPIO.input(pin)
            )

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_toggle,
                bouncetime=20
            )

    def test_sensors(self):
        """
        Print message upon contact of any touch sensor.
        """
        print("Testing all touch sensors.")

        spout_pins = [i['touch'] for i in self.spouts]

        def _print_touch(pin):
            if pin == self.paw_pins[0]:
                print(f"Left:    {GPIO.input(pin)}")
            elif pin == self.paw_pins[1]:
                print(f"Right:   {GPIO.input(pin)}")
            else:
                print("Spout %s:    {GPIO.input(pin)}" %
                      spout_pins.index(pin))

        for pin in self.paw_pins + spout_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_print_touch,
                bouncetime=10
            )

    def toggle_spout_leds(self):
        """
        Toggle the target spout LEDs with the buttons.
        """
        print("Push button to toggle corresponding LED.")

        led_pins = [i['cue'] for i in self.spouts]

        def _toggle(pin):
            spout_number = self._button_pins.index(pin)
            state = GPIO.input(led_pins[spout_number])
            GPIO.output(led_pins[spout_number], not state)

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_toggle,
                bouncetime=300
            )

    def test_reward_volume(self):
        """
        Measure volume of water being dispensed for a specified dispense
        duration.
        """

        duration_ms = int(input("Specify duration to dispense in ms: "))
        print("Press button to dispense from corresponding spout.")

        def _dispense(pin):
            self.dispense_water(
                self._button_pins.index(pin),
                duration_ms
            )

        GPIO.add_event_detect(
            self._button_pins,
            GPIO.FALLING,
            callback=_dispense,
            bouncetime=1000
        )
