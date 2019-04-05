#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Spout definitions and functions
#


## Libraries ##
import RPi.GPIO as GPIO
import random
from time import sleep

# external
import external.gertbot as gertbot


## Spout class ##
class Spout(object):
    """ Handle raspberry pi pins and functions to control a water spout """

    def __init__(self, cue, touch, water):
        """ Sets up a spout and initialises Pi pins """
        self.cue = cue
        self.touch = touch
        self.water = water
        GPIO.setup(self.cue, GPIO.OUT, initial=False)
        GPIO.setup(self.touch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.water, GPIO.OUT, initial=False)

    def dispense(self, reward_ms):
        GPIO.output(self.water, True)
        sleep(reward_ms / 1000)
        GPIO.output(self.water, False)

    def open(self):
        GPIO.output(self.water, True)

    def close(self):
        GPIO.output(self.water, False)

    def set_cue(self, state):
        GPIO.output(self.cue, state)


## Select spout for trial ##
def select_spout(spout_count):
    new_spout = random.randint(0, spout_count)
    return new_spout


## Control stepper motor ##

board = 3
channel = 0
mode = 24
frequency = 900.0
steps = 200
gertbot.open_uart(0)

gertbot.set_mode(board, channel, mode)
gertbot.freq_stepper(board, channel, mode)

def present():
    gertbot.move_stepper(board, channel, steps)

def retract():
    gertbot.move_stepper(board, channel, -steps)

#TODO: add end stops? - see notes on yellow sheet
