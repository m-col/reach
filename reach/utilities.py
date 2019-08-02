#!/usr/bin/env python3
""" Misc utilities to test the reach rig """


import RPi.GPIO as GPIO
from time import sleep, time, strftime
import sys
from reach.raspberry import Pi


def use_utility(utility):
    """ Handle specified utility """

    if utility != 'list':
        print("Utility: %s" % utility)

    if utility == 'list':
        list_utils()

    elif utility == 'solenoid':
        solenoid()

    elif utility == 'sensors':
        touch_sensors()

    elif utility == 'cues':
        cues()

    else:
        print("Util '%s' does not exit" % utility)
        sys.exit(1)

    sys.exit(0)


def list_utils():
    """ List available utilities """
    print("Available utilities:")
    print("solenoid     - open or close a solenoid")
    print("sensors      - test paw and spout touch sensors")
    print("cues         - test spout LEDs")



def solenoid():
    """ Open or close solenoid using push button """

    # Add a second spout when the hardware exists
    pi = Pi(1)

    num_spouts = len(pi.spouts)
    if num_spouts > 1:
        print("Number of spouts: %s" % num_spouts)
        spout_num = input("Select spout (0-%s): " % num_spouts - 1)
    else:
        spout_num = 0

    print("Hold button to open solenoid")
    print("Hit Control-C to quit")

    def toggle(pin):
        """ Set solenoid pin to inverse of start button pin """
        sleep(0.010)
        GPIO.output(
                pi.spouts[spout_num].water,
                not GPIO.input(pi.start_button)
                )

    GPIO.add_event_detect(
            pi.start_button,
            GPIO.BOTH,
            callback=toggle,
            bouncetime=20
            )

    while True:
        sleep(1)



def touch_sensors():
    """ Test paw and spout capacitive touch sensors """

    pi = Pi(1)

    def print_touch(pin):
        if pin == pi.paw_r:
            print("Right:    %i" % GPIO.input(pin))
        elif pin == pi.paw_l:
            print("Left:    %i" % GPIO.input(pin))
        else:
            for i in range(len(pi.spouts)):
                if pi.spouts[i-1].touch == pin:
                    spout_num = i+1
                    print("Spout %i:    %s" %
                            (spout_num,
                            GPIO.input(pin)))
                    break

    # listen to touches on paw rests
    GPIO.add_event_detect(pi.paw_r, GPIO.BOTH,
        callback=print_touch, bouncetime=10)

    GPIO.add_event_detect(pi.paw_l, GPIO.BOTH,
        callback=print_touch, bouncetime=10)

    # listen to touches to spouts
    for spout in pi.spouts:
        print("PIN: %i" % spout.touch)
        GPIO.add_event_detect(
                spout.touch, GPIO.BOTH,
                callback=print_touch, bouncetime=10
                )

    input("Hit enter or Control-C to quit\n")
    while True:
        sleep(1)



def cues():
    """ Test spout LEDs """

    # Add a second spout when the hardware exists
    pi = Pi(1)

    num_spouts = len(pi.spouts)
    if num_spouts > 1:
        print("Number of spouts: %s" % num_spouts)
        spout_num = input("Select spout (0-%s): " % num_spouts - 1)
    else:
        spout_num = 0

    print("Push button to toggle LED cue")
    print("Hit Control-C to quit")

    def toggle(pin):
        """ Toggle specified LED """
        state = GPIO.input(pi.spouts[spout_num].cue)
        GPIO.output(pi.spouts[spout_num].cue, not state)

    GPIO.add_event_detect(pi.start_button, GPIO.FALLING,
        callback=toggle, bouncetime=300)
    
    while True:
        sleep(1)
