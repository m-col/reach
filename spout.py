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
        GPIO.setup(self.cue, GPIO.OUT)
        GPIO.setup(self.touch, GPIO.IN)
        GPIO.setup(self.water, GPIO.OUT)

    def dispense(reward_ms):
        GPIO.output(self.water, ON)
        sleep(reward_ms)
        GPIO.output(self.water, OFF)


## Select spout for trial ##
def select_spout(spout_count):
    new_spout = random.randint(0, spout_count)
    return new_spout
