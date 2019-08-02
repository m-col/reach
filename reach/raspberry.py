#!/usr/bin/env python3
""" Helper functions and classes """



import signal, sys, time
import RPi.GPIO as GPIO



class Spout(object):
    """ Handle a single spout with cue, touch sensor and water """

    def __init__(self, cue, touch, water):
        """ Set up a spout and initialise its pins """
        self.cue = cue
        self.touch = touch
        self.water = water
        GPIO.setup(cue, GPIO.OUT, initial=False)
        GPIO.setup(touch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(water, GPIO.OUT, initial=False)

        self.cue_t = []
        self.touch_t = []

    def dispense(self, duration_ms):
        """ Dispense water reward during training """
        GPIO.output(self.water, True)
        time.sleep(duration_ms / 1000)
        GPIO.output(self.water, False)



class Pi(object):
    """ An instance of a raspberry pi and its pins """

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    def __init__(self, spout_count):
        self.start_button = 4
        GPIO.setup(
                self.start_button,
                GPIO.IN,
                pull_up_down=GPIO.PUD_UP
                )

        self.paw_l = 17
        self.paw_r = 18
        GPIO.setup(
                [self.paw_l, self.paw_r],
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN
                )

        self.spouts = []
        if spout_count == 1:
            # pins for cue, touch sensor, water dispensor
            self.spouts.append(Spout(5, 27, 25))     
        elif spout_count > 1:
            print("Pins described for only one spout")
            helpers.clean_exit(1)

        signal.signal(
                signal.SIGINT,
                self.cleanup
                )

    def cleanup(self, signum=0, frame=0):
        """ Unitialise pins for clean exit """
        for spout in self.spouts:
            GPIO.output(spout.water, False)
        GPIO.cleanup()
        sys.exit(signum)

