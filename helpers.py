#!/usr/bin/env python3
#
# Helper definitions for reach task control
#


## Libraries ##
import RPi.GPIO as GPIO
import sys


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

    def dispense(water_period):
        GPIO.output(self.water, ON)
        sleep(water_period)
        GPIO.output(self.water, OFF)


## Signal handler ##
def handle_signal(sig, frame):
    GPIO.cleanup()
    sys.exit()
