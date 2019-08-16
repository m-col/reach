#!/usr/bin/env python3
""" Misc utilities to test the reach rig """


from time import sleep
import sys
from reach.raspberry import Pi

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import PPi.GPIO as GPIO


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

    elif utility == 'reward':
        reward_vol()

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
    print("reward       - dispense water at reward volumes")


def solenoid():
    """ Open or close solenoid using push button """

    # Add a second spout when the hardware exists
    num_spouts = 1
    pi = Pi(num_spouts)

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

    # Add a second spout when the hardware exists
    num_spouts = 1
    pi = Pi(num_spouts)

    def print_touch(pin):
        if pin == pi.paw_r:
            print("Right:    %i" % GPIO.input(pin))
        elif pin == pi.paw_l:
            print("Left:    %i" % GPIO.input(pin))
        else:
            for i in range(len(pi.spouts)):
                if pi.spouts[i - 1].touch == pin:
                    spout_num = i + 1
                    print("Spout %i:    %s"
                          % (spout_num, GPIO.input(pin)))
                    break

    # listen to touches on paw rests
    GPIO.add_event_detect(
        pi.paw_r, GPIO.BOTH, callback=print_touch, bouncetime=10
    )

    GPIO.add_event_detect(
        pi.paw_l, GPIO.BOTH, callback=print_touch, bouncetime=10
    )

    # listen to touches to spouts
    for spout in pi.spouts:
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
    num_spouts = 1
    pi = Pi(num_spouts)

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


def reward_vol():
    """ Measure volume of water dispensed during rewards """

    # Add a second spout when the hardware exists
    num_spouts = 1
    pi = Pi(num_spouts)

    if num_spouts > 1:
        print("Number of spouts: %s" % num_spouts)
        spout_num = input("Select spout (0-%s): " % num_spouts - 1)
    else:
        spout_num = 0

    duration_ms = int(input("Specify duration to open solenoid in ms: "))
    print("Press button to dispense reward volume")
    print("Hit Control-C to quit")

    def dispense(pin):
        """ Set solenoid pin to inverse of start button pin """
        pi.spouts[spout_num].dispense(duration_ms)

    GPIO.add_event_detect(
        pi.start_button,
        GPIO.FALLING,
        callback=dispense,
        bouncetime=1000
    )

    while True:
        sleep(1)
