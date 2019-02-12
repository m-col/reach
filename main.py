#!/usr/bin/env python3
#
# Main control script for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO         # raspberry pi pins
from time import sleep, time, strftime
import signal
import random
import sys

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

paw_l = 17          # left paw touch sensor
paw_r = 27          # right paw touch sensor
start_button = 25   # start button used to begin task

GPIO.setup(paw_l, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(paw_r, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(start_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
success = False
current_spout = None

# Record start time
p.start_time = time()
p.end_time = p.start_time + p.duration * 60
now = p.start_time

# Start keeping track of performance
reward_count = 0
missed_count = 0
trial_count = 0
spont_count = 0

# get metadata
if save_metadata:
    metadata, mouseID = helpers.request_metadata()


## State 1 - inter-trial interval ##
iti_broken = False
iti_break_count = 0

def iti_break(pin):
    global iti_broken
    iti_broken = True
    global iti_break_count
    iti_break_count += 1

def inc_sponts(pin):
    global spont_count
    spont_count += 1

def iti(p, current_spout):
    is_iti = True
    global iti_broken

    # start watching for paws moving from rest position
    GPIO.add_event_detect(paw_r, GPIO.FALLING,
            callback=iti_break, bouncetime=300)
    GPIO.add_event_detect(paw_l, GPIO.FALLING,
            callback=iti_break, bouncetime=300)

    # start watching for spontaneous reaches to spout
    GPIO.add_event_detect( spouts[current_spout - 1].touch,
            GPIO.FALLING, callback=inc_sponts, bouncetime=300 )

    while is_iti:
        iti_broken = False
        ITI_duration = random.uniform(p.ITI_min_ms, p.ITI_max_ms) / 1000
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

    GPIO.remove_event_detect(paw_r)
    GPIO.remove_event_detect(paw_l)
    GPIO.remove_event_detect(spouts[current_spout - 1].touch)
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

# add tiemr signal here instad of polling?
    while not success and now < cue_end:
        sleep(0.01)
        now = time()

    # Disable cue if it was a missed trial
    GPIO.output(spouts[current_spout - 1].cue, False)

    # Remove spout contact detection
    GPIO.remove_event_detect( spouts[current_spout - 1].touch )

    # We need to sleep at the same time as a reward
    if success:
        sleep(p.reward_ms / 1000)

    return success


## State 3 - reward period ##
def reward(pin, var=1):
    GPIO.output(spouts[current_spout - 1].cue, False)
    GPIO.output(spouts[current_spout - 1].water, True)
    global success
    success = True
    sleep(p.reward_ms / 1000)
    GPIO.output(spouts[current_spout - 1].water, False)


## Main ##
print("Hit the start button to begin.")
GPIO.wait_for_edge(start_button, GPIO.FALLING)

#while now < p.end_time:
if True:
    trial_count += 1
    print("_________________________________")
    print("# ----- Starting trial #%i ----- #"
            % trial_count)

    # reset success
    success = False

    # select a spout for this trial
    current_spout = spout.select_spout(p.spout_count)

    # run inter-trial interval
    iti(p, current_spout)

    # initiate cued reach
    success = trial(p, current_spout)

    # deal with outcome
    if success:
        print("Successful reach!")
        reward_count += 1
    else:
        print("Missed reach")
        missed_count += 1

    print("Total rewards: %i" % reward_count)
    now = time()


## Finish ##
print("""_________________________________

# __________ The end __________ #

Totals:
    Trials:                 %i
    Rewarded reaches:       %i (%0.1f%%)
    Missed cues:            %i (%0.1f%%)
    Spontaneous reaches:    %i
    ITI resets:             %i
    """ % (trial_count, reward_count, 100*reward_count/trial_count,
        missed_count, 100*missed_count/trial_count,
        spont_count, iti_break_count))

if save_metadata:
    # save metadata to mouse training JSON
    p.trial_count   = trial_count
    p.reward_count  = reward_count
    p.missed_count  = missed_count
    p.spont_count   = spont_count
    p.resets        = iti_break_count

    helpers.write_metadata(metadata, mouseID, p)

print("\nGoodbye!\n")

exit(0)
