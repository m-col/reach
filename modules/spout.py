#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Spout definitions and functions
#


## Libraries ##
import RPi.GPIO as GPIO
import random
from time import sleep


## Spout class ##
class Spout(object):
    """ Handle raspberry pi pins and functions to control a water spout """

    def __init__(self, cue, touch, water):
        """ Sets up a spout and initialises Pi pins """
        self.cue = cue
        self.touch = touch
        self.water = water
        GPIO.setup(cue, GPIO.OUT, initial=False)
        GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(water, GPIO.OUT, initial=False)

        # also keep track of timepoints
        self.t_cue = []
        self.t_touch = []
        self.t_release = []

    def open(self):
        """ Dispense water. This is used for testing. """
        GPIO.output(self.water, True)

    def close(self):
        """ Stop dispensing water. This is used for testing. """
        GPIO.output(self.water, False)

    def cue_toggle(self, pin):
        """ Toggle LED. This is used for testing. """
        state = not GPIO.input(self.cue)
        GPIO.output(self.cue, state)

    def dispense(self, reward_ms):
        """ Dispense water reward during training """
        GPIO.output(self.water, True)
        sleep(reward_ms / 1000)
        GPIO.output(self.water, False)

    def release(self, pin):
        """ Increment release of spout as callback for touch
        sensor event detect """
        self.t_release.append(time())


## Select spout for trial ##
def select_spout(spout_count):
    new_spout = random.randint(0, spout_count - 1)
    return new_spout
