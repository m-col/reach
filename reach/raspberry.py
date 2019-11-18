"""
Raspberry Pis
=============

The RPiReal object represents a raspberry pi and directly controls GPIO pins
used to operate the training box hardware during behavioural training.

The _RPiMock object represents the same as RPiReal except never handles any
hardware, acting as a mock raspberry pi.

Upon import of this module, we check if we can import RPI.GPIO. If we can, we
export RPi as RPiReal, else as _RPiMock.

"""
# pylint: disable=unused-argument,arguments-differ


import time

_IS_RASPBERRY_PI = True
try:
    import RPi.GPIO as GPIO  # pylint: disable=import-error
except ModuleNotFoundError:
    _IS_RASPBERRY_PI = False


_PIN_NUMBERS = {
    'buttons': (2, 3, 4, 7),
    'paw_sensors': (5, 6),
    'air_puff': 18,
    'spouts': (
        {
            'cue': 23,
            'touch': 14,
            'solenoid': 16,
            'actuator': 12,
        },
        {
            'cue': 22,
            'touch': 15,
            'solenoid': 21,
            'actuator': 13,
        },
    ),
}

_DUTY_CYCLES = (
    5.9, 6.15, 6.45, 6.65, 6.86, 7.1, 7.35,
)


class Spout:
    """
    This object represents and controls a single target spout.

    Parameters
    ----------
    spout_number : int
        The spout number assigned to this spout (either 0 or 1).

    """
    def __init__(self, spout_number):
        pin_numbers = _PIN_NUMBERS['spouts'][spout_number]
        self.cue = pin_numbers['cue']
        self.touch = pin_numbers['touch']
        self.solenoid = pin_numbers['solenoid']
        self.actuator = pin_numbers['actuator']

        GPIO.setup(self.cue, GPIO.OUT, initial=False)
        GPIO.setup(self.touch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.solenoid, GPIO.OUT, initial=False)
        GPIO.setup(self.actuator, GPIO.OUT, initial=False)

        self._duty_cycle = 0
        self._pwm = GPIO.PWM(self.actuator, 50)
        self._pwm.start(self._duty_cycle)

    @property
    def duty_cycle(self):
        """
        Keep track of actuator PWM duty cycle.
        """
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, duty_cycle):
        """
        Set duty cycle of actuator PWM.
        """
        self._duty_cycle = duty_cycle
        self._pwm.ChangeDutyCycle(duty_cycle)
        #time.sleep(1)
        #self._pwm.ChangeDutyCycle(0)

    def disable(self):
        """
        Disable actuator PWM and close solenoid valve.
        """
        self._pwm.stop()
        GPIO.output(self.solenoid, False)


class RPiReal:
    """
    An instance of a raspberry pi and its GPIO pins.

    Parameters
    ----------
    spout_count : int
        The number of spouts to be used for the current training session.

    Attributes
    ----------
    _button_pins : list of 2 ints
        The pin numbers that listen to the left and right buttons.

    paw_pins : list of 2 ints
        The pin numbers that listen to the left and right paw rests.

    spouts : list of dicts
        List containing, for len(spouts) spouts, dicts listing the pin numbers
        for each spout's cue, touch and solenoid pins, and spout position in mm
        from mouse.

    _air_puff : int
        Pin number that controls the air puff solenoid.

    """
    def __init__(self, spout_count):
        """
        Initialise the pi and set initial pin states.

        Parameters
        ----------
        spout_count : int
            The number of spouts to be used for the current training session.

        """
        self._button_pins = _PIN_NUMBERS['buttons']
        self.paw_pins = _PIN_NUMBERS['paw_sensors']
        self._air_puff = _PIN_NUMBERS['air_puff']

        self.spouts = []
        self._spout_position = 0
        self._initialise_pins()

    def _initialise_pins(self):
        """
        Set initial state of pins.
        """

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(
            self._button_pins,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP,
        )

        GPIO.setup(
            self.paw_pins,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN,
        )

        GPIO.setup(
            self._air_puff,
            GPIO.OUT,
            initial=False,
        )

        self.spouts.append(Spout(0))
        self.spouts.append(Spout(1))

    def wait_to_start(self):
        """
        Block the program and wait until the enter key is hit. Once this is
        pressed, the training session begins.
        """
        try:
            input("Press enter to begin.\n")
            return True
        except KeyboardInterrupt:
            return False

    def monitor_sensors(self, reset_iti, increase_spont_reaches):
        """
        Monitor touch sensors during the inter-trial interval to execute
        callback functions upon movement events.

        Parameters
        ----------
        reset_iti : func
            Callback function executed upon lift of either paw.

        increase_spont_reaches : func
            Callback function executed upon contact with any spout touch
            sensors.

        """
        for paw in self.paw_pins:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=reset_iti,
                bouncetime=100,
            )

        for spout in self.spouts:
            GPIO.add_event_detect(
                spout.touch,
                GPIO.RISING,
                callback=increase_spont_reaches,
                bouncetime=100,
            )

    def set_button_callback(self, button, func):
        """
        Add a callback function to be executed upon button press.

        Parameters
        ----------
        button : int
            The number of the button to assign the function to (zero-indexed).

        callback_function : func
            Function to be executed upon button press.

        """
        GPIO.remove_event_detect(self._button_pins[button])
        GPIO.add_event_detect(
            self._button_pins[button],
            GPIO.FALLING,
            callback=func,
            bouncetime=500
        )

    @property
    def spout_position(self):
        """
        Keep track of spout actuator position.
        """
        return self._spout_position

    @spout_position.setter
    def spout_position(self, pos):
        """
        Change spout position by assignment.

        The _spout_position attribute and this property represent distance in
        mm from the mouse, and is limited to between 1 and 7 mm.
        """
        if pos < 1:
            pos = 1
        elif pos > 7:
            pos = 7

        duty_cycle = _DUTY_CYCLES[pos - 1]
        for spout in self.spouts:
            spout.duty_cycle = duty_cycle

        self._spout_position = pos

    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        print("Waiting for rest... ")
        try:
            while not all([GPIO.input(self.paw_pins[0]),
                           GPIO.input(self.paw_pins[1])]):
                time.sleep(0.010)
        except RuntimeError:
            # Ignore GPIO error when Ctrl-C cancels training
            pass

    def disable_callbacks(self):
        """
        Remove event detection from all touch sensors at the end of the
        inter-trial interval.
        """
        for pin in self.paw_pins:
            GPIO.remove_event_detect(pin)

        for pin in self._button_pins:
            GPIO.remove_event_detect(pin)

        for spout in self.spouts:
            GPIO.remove_event_detect(spout.touch)

    def start_trial(self, spout_number, lift_func, reward_func, incorrect_func):
        """
        Illuminate a cue, record the time, and add callback functions to be
        executed upon grasp of target spouts during trial.

        Parameters
        ----------
        spout_number : int
            The spout number corresponding to this trial's reach target.

        reward_func : func
            Callback function to be executed upon successful grasp of target
            spout.

        incorrect_func : func
            Callback function to be executed upon incorrect grasp of non-target
            spout.

        """
        print("Cue illuminated")
        GPIO.output(self.spouts[spout_number].cue, True)

        for paw_pin in self.paw_pins:
            GPIO.add_event_detect(
                paw_pin,
                GPIO.FALLING,
                callback=lift_func,
                bouncetime=1000,
            )

        GPIO.add_event_detect(
            self.spouts[spout_number].touch,
            GPIO.RISING,
            callback=reward_func,
            bouncetime=1000,
        )

        if len(self.spouts) > 1:
            GPIO.add_event_detect(
                self.spouts[1 - spout_number].touch,
                GPIO.RISING,
                callback=incorrect_func,
                bouncetime=1000,
            )

    def dispense_water(self, spout_number, duration_ms):
        """
        Dispense water from a specified spout.

        Parameters
        ----------
        spout_number : int
            The spout number to dispense water from i.e. 0=left, 1=right.

        duration_ms : int
            The duration in milliseconds to open the solenoid.

        """
        GPIO.output(self.spouts[spout_number].solenoid, True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self.spouts[spout_number].solenoid, False)

    def miss_trial(self, duration_ms=30):
        """
        Trigger air puff to remove non-collected water at the end of a missed
        trial.
        """
        GPIO.output(self._air_puff, True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self._air_puff, False)

    def end_trial(self):
        """
        Disable target spout LED and remove spout touch sensors event
        callbacks.
        """
        self.disable_callbacks()
        for spout in self.spouts:
            GPIO.output(spout.cue, False)

    def cleanup(self, signal_number=None, frame=None):
        """
        Clean up and uninitialise pins.

        Parameters
        ----------
        signal_number : int, optional
            Passed to function by signal.signal; ignored.

        frame : int, optional
            Passed to function by signal.signal; ignored.

        """
        for spout in self.spouts:
            spout.disable()
        GPIO.cleanup()


class _RPiMock(RPiReal):
    """
    A mock instance of a raspberry pi and its GPIO pins. This class is a
    fallback for .RPiReal when the RPi.GPIO library cannot be loaded, which
    assumes that we are working on a non-raspberry pi machine for development.

    This subclass overrides most methods to replace all calls to RPi.GPIO that
    the superclass would otherwise execute.
    """
    def _initialise_pins(self):
        pass

    def wait_to_start(self):
        """
        Instead of blocking execution, simply print a message.
        """
        print("Press enter to begin.")
        return True

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
        print("Waiting for rest... ")
        time.sleep(1)

    def disable_callbacks(self):
        """
        Pretend to remove event detection from all touch sensors at the end of
        the inter-trial interval.
        """

    def start_trial(self, spout_number, *args, **kwargs):
        """
        Record the trial start time.

        Parameters
        ----------
        spout_number : int
            The spout number corresponding to this trial's hypothetical reach
            target.

        """
        print("Cue illuminated")

    def dispense_water(self, spout_number, duration_ms):
        """
        Pretend to dispense water from a specified spout.

        Parameters
        ----------
        spout_number : int
            The spout number that would dispense water if this were real.

        duration_ms : int
            The duration in milliseconds to wait pretending to dispense.

        """
        time.sleep(duration_ms / 1000)

    def miss_trial(self):
        """
        Wait during air puff period.
        """
        time.sleep(0.030)

    def end_trial(self):
        """
        Pretend to disable target spout LED and remove spout touch sensors
        event callbacks.
        """

    def cleanup(self):
        """
        Pretend to clean up and uninitialise pins.
        """


RPi = RPiReal if _IS_RASPBERRY_PI else _RPiMock


class UtilityPi(RPiReal):
    """
    A representation of a Raspberry Pi that exposes methods that serve as
    utilities for testing the training hardware.

    """

    def __init__(self):
        """
        This subclass interacts with both spouts so initialises as
        :class:`._RPi` with two spouts.
        """
        super().__init__(2)

    def hold_open_solenoid(self):
        """
        Hold open a target's solenoid continuous while a button is held.
        """
        print("Hold a button to open the corresponding solenoid.")

        def _toggle(pin):
            time.sleep(0.010)
            GPIO.output(
                self.spouts[self._button_pins.index(pin)].solenoid,
                not GPIO.input(pin),
            )

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_toggle,
                bouncetime=20,
            )

    def test_sensors(self):
        """
        Print a message upon contact of any touch sensor.
        """
        print("Testing all touch sensors.")

        spout_pins = [i.touch for i in self.spouts]

        def _print_touch(pin):
            if pin == self.paw_pins[0]:
                print(f"Left:    {GPIO.input(pin)}")
            elif pin == self.paw_pins[1]:
                print(f"Right:   {GPIO.input(pin)}")
            else:
                print(
                    f"Spout {spout_pins.index(pin) + 1}:    {GPIO.input(pin)}"
                )

        for pin in self.paw_pins + spout_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=_print_touch,
                bouncetime=10
            )

    def toggle_spout_leds(self):
        """
        Toggle the two target spout LEDs with the two buttons.
        """
        print("Push button to toggle corresponding LED.")

        led_pins = [i.cue for i in self.spouts]

        def _toggle(pin):
            spout_number = self._button_pins.index(pin)
            state = GPIO.input(led_pins[spout_number])
            GPIO.output(led_pins[spout_number], not state)

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_toggle,
                bouncetime=500,
            )

    def test_reward_volume(self):
        """
        Measure volume of water dispensed by a specified dispense duration.
        """
        duration_ms = int(input("Specify duration to dispense in ms: "))
        print("Press button 0 or 1 to dispense from corresponding spout.")

        def _dispense(pin):
            self.dispense_water(
                self._button_pins.index(pin),
                duration_ms,
            )

        for pin in self._button_pins:
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
        duration_ms = int(input("Specify duration to puff air in ms: "))
        print("Press button 0 to trigger air puff.")
        print("Press button 1 to open solenoids.")

        GPIO.add_event_detect(
            self._button_pins[0],
            GPIO.FALLING,
            callback=lambda _: self.miss_trial(duration_ms=duration_ms),
            bouncetime=500,
        )

        def _toggle(pin):
            time.sleep(0.010)
            for spout in self.spouts:
                GPIO.output(
                    spout.solenoid,
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
        puff_duration_ms = int(input(
            "Specify duration to puff air in ms: "
        ))
        dispense_duration_ms = int(input(
            "Specify duration to dispense in ms: "
        ))
        print("Press button 0 to trigger air puff.")
        print(f"Press button 1 to dispense water for {dispense_duration_ms} ms.")

        GPIO.add_event_detect(
            self._button_pins[0],
            GPIO.FALLING,
            callback=lambda _: self.miss_trial(duration_ms=puff_duration_ms),
            bouncetime=500,
        )

        def _dispense(pin):
            time.sleep(0.010)
            for spout_number in [0, 1]:
                self.dispense_water(
                    spout_number,
                    dispense_duration_ms,
                )

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

    def test_actuators(self):
        """
        Move the actuator positions using the buttons.
        """
        print("Press button 0 or 1 to advance or retract the actuators by 1 step.")
        print("Press button 2 or 3 to advance or retract the actuators fully.")

        def _move_spouts(pin):
            button_num = self._button_pins.index(pin)
            if button_num == 0:
                self.spout_position -= 1
            if button_num == 1:
                self.spout_position += 1
            if button_num == 2:
                self.spout_position = 0.5
            if button_num == 3:
                self.spout_position = 14
            print(f'Spout position: {self.spout_position}')

        for pin in self._button_pins:
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=_move_spouts,
                bouncetime=1000,
            )

        self.spout_position = 1
