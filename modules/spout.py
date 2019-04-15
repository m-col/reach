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
        GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(water, GPIO.OUT, initial=False)
        self.sponts = []

        # also keep track of timepoints
        self.t_cue = []
        self.t_touch = []
        self.t_release = []

    def open(self):
        """ Open solenoid. This is used for testing. """
        GPIO.output(self.water, True)

    def close(self):
        """ Close solenoid. This is used for testing. """
        GPIO.output(self.water, False)


    def set_cue(self, state='toggle'):
        """ Enable or disable LED cue """
        self.t_cue.append(time())
        if state == 'toggle':
            state = not GPIO.input(self.cue)
        GPIO.output(self.cue, state)

    def dispense(self, reward_ms):
        """ Dispense water reward during training """
        self.open()
        sleep(reward_ms / 1000)
        self.close(


## Select spout for trial ##
def select_spout(spout_count):
    new_spout = random.randint(0, spout_count - 1)
    return new_spout
