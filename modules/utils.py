#!/usr/bin/env python3
#
# Utilities for mouse reach task control
#

## Libraries
import RPi.GPIO as GPIO
from time import sleep, time, strftime

# external
import external.gertbot

# custom modules
import modules.helpers as helpers


## Utility helper
def use_util(settings, p, spouts):
    util = settings['utility']
    print("Utility: %s" % util)

    if util == 'list':
        list_utils()

    elif util == 'solenoid':
        solenoid(p, spouts)

    elif util == 'paws':
        paws(p)

    else:
        print("Util '%s' does not exit" % util)
        helpers.clean_exit(1)

    helpers.clean_exit(0)


## List utilities
def list_utils():
    print("Available utilities:")
    print("solenoid - open solenoid")
    print("paws     - test paw rest touch sensors")


## Open solenoid
def solenoid(p, spouts):
    if len(spouts) > 1:
        print("Number of spouts: %s" % len(spouts))
        num = input("Select spout: ")
    else:
        num = 0

    print("Hold start button to open spout")
    print("and hit ctrl-C to finish")
    while True:
        if GPIO.input(p.start_button):
            spouts[num].close()
        else:
            spouts[num].open()
        sleep(0.02)


## Test paw rest touch sensors
def paws(p):
    """ Test paw rest touch sensors """

    def read_paw_r(pin):
        print("Right:    %s" % GPIO.input(p.paw_r))

    def read_paw_l(pin):
        print("Left:    %s" % GPIO.input(p.paw_l))

    GPIO.add_event_detect(p.paw_r, GPIO.BOTH,
            callback=read_paw_r, bouncetime=100)

    GPIO.add_event_detect(p.paw_l, GPIO.BOTH,
            callback=read_paw_l, bouncetime=100)

    input("Hit enter or ctrl-c to quit\n")
    helpers.clean_exit(0)
