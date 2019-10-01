"""
Curses Interface
================

The RPiCurses object is a child class of reach.RPiReal that mimics a real
raspberry pi, but unlike the reach._RPiMock mock pi, _RPiCurses provides a
curses interface that can be used to perform the task in a terminal. This
allows for testing of new code that depends on interactivity of the task.

This file provides some additional functions to help manage the curses
interface.

"""


import curses
import textwrap
import time
import random

from reach.raspberry import RPiReal
import reach.drawings as drawings


def get_str_dims(string):
    """
    Get width and height of a multiline string.
    """
    height = string.count('\n')
    width = 0
    for substr in string.splitlines():
        if len(substr) > width:
            width = len(substr)
    return height, width


def addstr_multiline(win, y_pos, x_pos, string, attr=None):
    """
    Print multiline string to curses window to specified position.
    """
    if attr is None:
        for y, line in enumerate(string.splitlines()):
            win.addstr(
                y_pos + y,
                x_pos,
                line,
            )

    else:
        for y, line in enumerate(string.splitlines()):
            win.addstr(
                y_pos + y,
                x_pos,
                line,
                attr,
            )


class RPiCurses(RPiReal):
    """
    A mock instance of a raspberry pi and its GPIO pins. This class is a
    fallback for reach.RPiReal when the RPi.GPIO library cannot be loaded,
    which assumes that we are working on a non-raspberry pi machine. This class
    differs from reach._RPiMock in that this class provides a curses-based
    interface to interact with the mock task in a terminal window.

    This subclass overrides most methods to replace all calls to RPi.GPIO to
    instead keep track of hypothetical pin state changes.

    Attributes
    ----------
    _stdscr : curses.window object
        This is the screen window object returned from curses.initscr().

    _height : int
        Height in lines of the _stdscr screen.

    _width : int
        Width in columns of the _stdscr screen.

    _feed : curses.window object
        This window displays a feed of information during the training session.

    _rig : curses.window object
        This window displays the virtual training rig.

    """

    is_real = False

    def __init__(self, spout_count):
        """
        Initialise virtual raspberry pi and draw rig on screen.
        """
        super().__init__(spout_count)

        self._stdscr = self._initialise_curses()

        height, width = self._stdscr.getmaxyx()
        self._height = height
        self._width = width

        self._feed = curses.newwin(
            height - 18, width,
            0, 0,
        )
        self._feed.border()
        self._feed_text = [''] * (width - 2)
        
        self._rig, rig_x_pos = self._draw_rig()

        self._target_pos = (
            [7, rig_x_pos + 5],
            [7, rig_x_pos + 12],
        )

        self._draw_mouse()
        self._feed.refresh()
        self._rig.refresh()

    def _initialise_pins(self):
        """
        Set initial state of mock pins and virtual rig.
        """
        self._pin_states = [0] * 27
        for button in self._button_pins:
            self._pin_states[button] = 1

        for spout in self.spouts:
            spout['cue_timepoints'] = []
            spout['touch_timepoints'] = []

    def _initialise_curses(self):
        """
        Initialise curses settings. Returns the curses screen.
        """
        stdscr = curses.initscr()
        stdscr.keypad(True)

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.curs_set(0)
        curses.cbreak()
        curses.noecho()

        return stdscr

    def _draw_rig(self):
        """
        Draw curses version of training rig.
        """
        rig = curses.newwin(
            17, self._width,
            int(self._height - 18), 0,
        )
        rig.border()

        _, rig_width = get_str_dims(drawings.RIG_TEMPLATE)
        rig_x_pos = int(self._width/2 - rig_width/2)
        addstr_multiline(
            rig,
            2,
            rig_x_pos,
            drawings.RIG_TEMPLATE,
        )

        addstr_multiline(
            rig,
            11,
            3,
            drawings.BUTTONS,
        )

        return rig, rig_x_pos

    def _draw_mouse(self):
        """
        Draw mouse ASCII art in corner of rig window.
        """
        mouse = random.choice(drawings.MICE)
        dims = [i + 2 for i in get_str_dims(mouse)]
        y_pos = int(17 - dims[0])
        x_pos = self._width - dims[1]

        for y, line in enumerate(mouse.splitlines()):
            self._rig.addstr(
                y_pos + y,
                x_pos,
                line,
            )

    def print_to_feed(self, string):
        """
        Print text to self._feed window, scrolling as needed.
        """
        for line in string.splitlines():
            self._feed_text.extend(
                textwrap.wrap(line, width=self._width - 6) or ['']
            )

        for y, line in enumerate(self._feed_text[-(self._height - 22):]):
            self._feed.addstr(y + 2, 3, line)
            self._feed.clrtoeol()

        self._feed.border()
        self._feed.refresh()

    def wait_to_start(self):
        """
        Instead of blocking execution, simply print a message.
        """
        self.print_to_feed("Hit button 1 to begin.")

        while True:
            press = self._feed.getkey()
            if press == '1':
                break

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
│
        """
        for paw in self.paw_pins:
            # execute reset_iti if either v or n are released
            reset_iti

        for spout in self.spouts:
            # execute increase_spont_reaches if either g or h are pressed
            increase_spont_reaches

    def set_button_callback(self, button, func):
        """
        Add a callback function to be executed upon virtual button press.

        Parameters
        ----------
        button : int
            The index of the button to assign the function to.

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


    def wait_for_rest(self):
        """
        Block execution and wait until both paw sensors are held.
        """
        self.print_to_feed("Waiting for rest... ")
        time.sleep(0.5)

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
        spout_number : int
            The spout number corresponding to this trial's hypothetical reach
            target.

        """
        self.print_to_feed("Cue illuminated")
        self.spouts[spout_number]['cue_timepoints'].append(time.time())

        for target in self._target_pos:
            addstr_multiline(
                self._rig,
                *target,
                drawings.TARGET,
                attr=curses.color_pair(1),
            )
        self._rig.refresh()

    def successful_grasp(self, spout_number):
        """
        Record the time upon successful cued grasp of hypothetical target
        spout.

        Parameters
        ----------
        spout_number : int
            The spout number corresponding to this trial's reach target.

        """
        self.spouts[spout_number]['touch_timepoints'].append(time.time())

    def incorrect_grasp(self, spout_number):
        """
        Record time upon grasp of fictional incorrect spout during mock trial.

        Parameters
        ----------
        spout_number : int
            The spout number corresponding to this trial's reach target.

        """
        self.spouts[1 - spout_number]['touch_timepoints'].append(time.time())

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

    def end_trial(self):
        """
        Pretend to disable target spout LED and remove spout touch sensors
        event callbacks.
        """

    def cleanup(self, signal_number=None, frame=None):
        """
        Restore terminal state.
        """
        self._stdscr.keypad(False)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        raise SystemError
