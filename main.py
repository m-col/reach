#!/usr/bin/env python3
#
# Main control script for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO         # raspberry pi pins
from datetime import datetime
from time import sleep, time
import signal, random, sys

# Custom modules
import spout, helpers, config


## Setup ##

# Set parameters
config_file_default = 'settings.ini'
config_file, save_metadata = helpers.parse_args(sys.argv[1:], config_file_default)
p = config.process_config(config_file, config_file_default)

# Pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

paw_l = 17       # left paw touch sensor
paw_r = 27       # right paw touch sensor
GPIO.setup(paw_l, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(paw_r, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

# initialise variables we want global access to
success = True
current_spout = None

# Record start time
p.start_time = time()
p.end_time = p.start_time + p.session_duration * 60
now = p.start_time

# Start keeping track of performance
reward_count = 0
missed_count = 0
trial_count = 0
spont_count = 0


## State 1 - inter-trial interval ##
global iti_broken
iti_broken = False

def iti_break(pin):
    global iti_broken
    iti_broken = True

def iti(p):
    GPIO.remove_event_detect(paw_r)
    is_iti = True
    GPIO.add_event_detect(paw_r, GPIO.FALLING,
            callback=iti_break, bouncetime=200)
    global iti_broken

    while is_iti:
        iti_broken = False
        ITI_duration = random.uniform(p.ITI_min, p.ITI_max)
        print("Counting down %.2fs" % ITI_duration)
        now = time()
        trial_start = now
        trial_end = trial_start + ITI_duration

        while now < trial_end and not iti_broken:
            sleep(0.02)
            now = time()

        if iti_broken:
            continue
        else:
            is_iti = False

    return


## State 2 - trial period ##
def trial(p, current_spout):
    # Activate cue
    GPIO.output( spouts[current_spout - 1].cue, True )

    # Detect contact with spout
    GPIO.add_event_detect( spouts[current_spout - 1].touch,
            GPIO.FALLING, callback=reward, bouncetime=4000 )

    # Count down allowed trial time
    now = time()
    cue_end = now + p.cue_ms/1000
    while not success and now < cue_end:
        sleep(0.1)

    # Disable cue if it was a missed trial
    GPIO.output(spouts[current_spout - 1].cue, False)

    # Remove spout contact detection
    GPIO.remove_event_detect( spouts[current_spout - 1].touch )

    return success


## State 3 - reward period ##
def reward(pin, two):
    print("pin %s: " % pin)
    print("two %s: " % two)
    GPIO.output(spouts[current_spout - 1].cue, False)
    GPIO.output(spouts[current_spout - 1].water, True)
    success = True
    sleep(p.reward_ms / 1000)
    GPIO.output(spouts[current_spout - 1].water, False)


## Main ##
while now < p.end_time:
    trial_count += 1
    print("_________________________________")
    print("# ----- Starting trial #%i ----- #" % trial_count)

    # select a spout for this trial
    current_spout = spout.select_spout(p.spout_count)

    # run inter-trial interval
    iti(p)

    # initiate cued reach
    success = trial(p, current_spout)

    if success:
        print("Successful reach!")
        reward(p, current_spout)
        reward_count += 1
    else:
        print("Missed reach")
        missed_count += 1

    print("Total rewards: %i" % reward_count)

    now = time()

    #GPIO.wait_for_edge(spouts[current_spout].touch, GPIO.FALLING)

##
""" sequence:

What do I want to be output?
Constant output channels:
 - paw_l
 - paw_r
 - spout_position
 + led, touch and water per spout

Metadata (and ignore with -n flag)
 - p struct info
 - config_file

"""
