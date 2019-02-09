#!/usr/bin/env python3
#
# Helper functions for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO
import sys


## Signal handler ##
def handle_signal(sig, frame):
    GPIO.cleanup()
    sys.exit()
