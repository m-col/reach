#!/usr/bin/env python3
""" Helper functions and classes """

# pylint: disable=import-error, unused-argument, fixme

import signal
import sys
import time
import RPi.GPIO as GPIO


def setup_spout(spout):
    """ Initialise pins for a single spout """

    GPIO.setup(spout['cue'], GPIO.OUT, initial=False)
    GPIO.setup(spout['touch'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(spout['solenoid'], GPIO.OUT, initial=False)

    spout['cue_t'] = []
    spout['touch_t'] = []


class Pi():
    """ An instance of a raspberry pi and its pins """

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    def __init__(self, spout_count):
        self.start_button = 4
        GPIO.setup(
            self.start_button,
            GPIO.IN,
            pull_up_down=GPIO.PUD_UP
        )

        self.paws = [17, 18]
        GPIO.setup(
            self.paws,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN
        )

        self.spouts = []
        if spout_count == 1:
            self.spouts.append({
                'cue': 5,
                'touch': 27,
                'solenoid': 25,
            })

        elif spout_count == 2:
            print("Pins described for only one spout")
            self.cleanup(1)

        for spout in self.spouts:
            setup_spout(spout)

        signal.signal(
            signal.SIGINT,
            self.cleanup
        )

    def wait_to_start(self):
        """ Block until button is pressed """
        print("Hit the start button to begin.")
        GPIO.wait_for_edge(
            self.start_button,
            GPIO.FALLING
        )

    def wait_for_rest(self):
        """ Block until both paw sensors are held """
        print("Waiting for rest... ", end='', flush=True)
        # TODO: can GPIO.input be passed an array?
        while not all([GPIO.input(self.paws[0]),
                       GPIO.input(self.paws[1])]):
            time.sleep(0.020)

    def successful_grasp(self, spout_num):
        """ Disable LED and count touch time upon cued grasp """
        GPIO.output(self.spouts[spout_num]['cue'], False)
        self.spouts[spout_num]['touch_t'].append(time.time())

    def monitor_sensors(self, spout_num, iti_break, inc_sponts):
        """ Add event detects for all touch sensors during iti """
        for paw in self.paws:
            GPIO.add_event_detect(
                paw,
                GPIO.FALLING,
                callback=iti_break,
                bouncetime=100
            )

        GPIO.add_event_detect(
            self.spouts[spout_num]['touch'],
            GPIO.RISING,
            callback=inc_sponts,
            bouncetime=100
        )

    def reset_button_callback(self, func):
        """ Add event callback to button """
        GPIO.remove_event_detect(self.start_button)
        GPIO.add_event_detect(
            self.start_button,
            GPIO.FALLING,
            callback=func,
            bouncetime=500
        )

    def disable_sensors(self, spout_num):
        """ Remove event detection from sensors at end of iti """
        # TODO: can the array be passed directly?
        for pin in [self.paws, self.spouts[spout_num]['touch']]:
            GPIO.remove_event_detect(pin)

    def start_trial(self, spout_num, reward):
        """ Illuminate cue, record time, add reward event detect """
        print("Cue illuminated")
        self.spouts[spout_num]['cue_t'].append(time.time())
        GPIO.output(self.spouts[spout_num]['cue'], True)

        GPIO.add_event_detect(
            self.spouts[spout_num]['touch'],
            GPIO.RISING,
            callback=reward,
            bouncetime=1000
        )

    def end_trial(self, spout_num):
        """ Disable cue, remove reward event callback """

        GPIO.output(self.spouts[spout_num].cue, False)

        GPIO.remove_event_detect(
            self.spouts[spout_num]['touch']
        )

    def dispense(self, spout_num, duration_ms):
        """ Dispense water reward """
        GPIO.output(self.spouts[spout_num]['solenoid'], True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self.spouts[spout_num]['solenoid'], False)

    def cleanup(self, signum=0, frame=0):
        """ Unitialise pins for clean exit """
        for spout in self.spouts:
            GPIO.output(spout.water, False)
        GPIO.cleanup()
        sys.exit(signum)
