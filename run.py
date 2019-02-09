#!/usr/bin/env python3
#
# Main control script for reach task control
#


## Libraries
import RPi.GPIO as GPIO         # raspberry pi pins
from datetime import datetime
from time import sleep, time
import signal
from helpers import Spout, handle_signal


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

# Spouts
if spout_count == 1:
    spout1 = Spout(22, 23, 24)     # pins for cue, touch sensor, solenoid

# Trap signals
signal.signal(signal.SIGINT, handle_signal)

# Record start time
start_time = time()
end_time = start_time + session_duration * 60
now = start_time


## Main control
while now < end_time:
    sleep(1)
    now = time()


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
