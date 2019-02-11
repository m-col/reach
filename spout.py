#!/usr/bin/env python3
#
# Spout definitions for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO
import random


## Spout class ##
class Spout(object):
    """ Sets up a spout and initialises Pi pins """
    def __init__(self, cue, touch, water):
        self.cue = cue
        self.touch = touch
        self.water = water
        GPIO.setup(self.cue, GPIO.OUT, initial=False)
        GPIO.setup(self.touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.water, GPIO.OUT, initial=False)

    def dispense(reward_ms):
        GPIO.output(self.water, True)
        sleep(reward_ms)
        GPIO.output(self.water, False)


## Select spout for trial ##
def select_spout(spout_count):
    new_spout = random.randint(0, spout_count)
    return new_spout
