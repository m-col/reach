#!/usr/bin/env python3
#
# Main control script for reach task control
#


## Libraries
import RPi.GPIO as GPIO         # raspberry pi pins
from datetime import datetime
from time import sleep, time
import signal
import random
import sys

# Custom
import spout
import helpers
from config import process_config


## Setup
# Generate parameter structure from config
p = process_config()

# Pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

paw_l = 17       # left paw touch sensor
paw_r = 27       # right paw touch sensor
GPIO.setup(paw_l, GPIO.IN)
GPIO.setup(paw_r, GPIO.IN)

# Create spouts
spouts = []
if p.spout_count == 1:
    spouts.append(spout.Spout(22, 23, 24))     # pins for cue, touch sensor, solenoid
else:
    print("Pins described for only one spout")
    sys.exit(1)

# Trap INT signal
signal.signal(signal.SIGINT, helpers.handle_signal)

# initialise randomness
random.seed()

# Record start time
p.start_time = time()
p.end_time = p.start_time + p.session_duration * 60
now = p.start_time


## State 1 - inter-trial interval
def iti(p):
    print("Starting new trial")
    ITI_duration = random.uniform(p.ITI_min, p.ITI_max)
    outcome = True
    return outcome


## State 2 - trial period
def trial(p, current_spout):
    print("Current spout: %s. trial." % current_spout)


## State 3 - reward period
def reward(p, current_spout):
    print("Current spout: %s. reward." % current_spout)


## Main control
while now < p.end_time:
    # select a spout for this trial
    current_spout = spout.select_spout(p.spout_count)

    # start intertrial interval
    outcome = iti(p)

    sleep(1)
    now = time()


##
""" sequence:
1. ITI - static state
2. while count down n seconds with no change to paw_l and paw_r
3. if paw_l or paw_r change, move to 1; else continue to 4
4. Trial start - select spout from available spouts
    - add 1 to session trial count for live display
5. Move selected spout forward
6. Activate LED cue on selected spout
7. Monitor for break in paw_l or paw_r sensor, and record time
8. Monitor for detection of touch sensor of spout
    - When touch sensor touched, record time, disable LED and dispense water
9. Pause n seconds, retract spout
10. move to 1 to restart

What do I want to be output?
Constant output channels:
 - paw_l
 - paw_r
 - spout_position
 + led, touch and water per spout


"""
