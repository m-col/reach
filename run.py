#!/usr/bin/env python3
#
# Main control script for mouse reaching task 
#


## Libraries ##
import RPi.GPIO as GPIO     # raspberry pi pins
from datetime import datetime

# custom
import spout_functions


## Pin setup ##
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)

paw_l = 1       # left paw touch sensor
paw_r = 2       # right paw touch sensor
GPIO.setup(paw_l, GPIO.IN)
GPIO.setup(paw_r, GPIO.IN)

# Spout one
led_1 = 3       # LED cue
touch_1 = 4     # touch sensor
water_1 = 5     # solenoid reward dispenser
init_spout(led_1, touch_1, water_1)

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
