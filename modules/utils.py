#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Utilities
#

## Libraries
import RPi.GPIO as GPIO
from time import sleep, time, strftime

# custom modules
import modules.helpers as helpers


## Utility helper
def use_util(settings, p, spouts):
    util = settings['utility']
    print("Utility: %s" % util)

    if util == 'list':
        list_utils()

    elif util == 'water':
        water(p, spouts)

    elif util == 'sensors':
        touch_sensors(p, spouts)

    elif util == 'cues':
        cues(p, spouts)

    else:
        print("Util '%s' does not exit" % util)
        helpers.clean_exit(1)

    helpers.clean_exit(0)


## List utilities
def list_utils():
    print("Available utilities:")
    print("water - dispense water")
    print("sensors  - test paw and spout touch sensors")
    print("cues     - test spout LEDs")


## Dispense water
def water(p, spouts):
    """ Dispense water using push button """

    if len(spouts) > 1:
        print("Number of spouts: %s" % len(spouts))
        num = input("Select spout: ")
    else:
        num = 0

    print("Hold button to dispense water")
    print("and hit ctrl-C to finish")
    while True:
        if GPIO.input(p.start_button):
            spouts[num].close()
        else:
            spouts[num].open()
        sleep(0.02)


## Test touch sensors
def touch_sensors(p, spouts):
    """ Test paw and spout touch sensors """

    def print_touch(pin):
        if pin == p.paw_r:
            print("Right:    %i" % GPIO.input(pin))
        elif pin == p.paw_l:
            print("Left:    %i" % GPIO.input(pin))
        else:
            for i in range(len(spouts)):
                if spouts[i-1].touch == pin:
                    spout_num = i+1
                    print("Spout %i:    %s" %
                            (spout_num,
                            GPIO.input(pin)))
                    break

    # listen to touches on paw rests
    GPIO.add_event_detect(p.paw_r, GPIO.BOTH,
        callback=print_touch, bouncetime=10)

    GPIO.add_event_detect(p.paw_l, GPIO.BOTH,
        callback=print_touch, bouncetime=10)

    # listen to touches to spouts
    for spout in spouts:
        GPIO.add_event_detect(
                spout.touch, GPIO.FALLING,
                callback=print_touch, bouncetime=10
                )

    input("Hit enter or ctrl-c to quit\n")
    helpers.clean_exit(0)


## Test LED cues
def cues(p, spouts):
    """ Test spout LEDs """

    if len(spouts) > 1:
        print("Number of spouts: %s" % len(spouts))
        num = input("Select spout to test: ")
    else:
        num = 0

    print("Push button to toggle LED cue")
    print("and hit ctrl-C to finish")

    def toggle_LED(pin):
        spouts[num].set_cue('toggle')

    GPIO.add_event_detect(p.start_button, GPIO.FALLING,
        callback=toggle_LED, bouncetime=300)
    
    while True:
        sleep(1)
