#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Main script
#


## Libraries ##
import RPi.GPIO as GPIO
from time import sleep, time, strftime
import signal
import random
import sys

# custom modules
import modules.config as config
import modules.helpers as helpers
import modules.spout as spout
import modules.utils as utils


## Setup ##

# set settings and parameters
settings = helpers.parse_args(sys.argv[1:])
p = config.process_config(settings)

# pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

p.paw_l = 18          # left paw touch sensor
p.paw_r = 23          # right paw touch sensor
p.start_button = 4   # start button used to begin task

GPIO.setup(p.paw_l, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(p.paw_r, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(p.start_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# create spouts
spouts = []
if p.spout_count == 1:
    # pins for cue, touch sensor, water dispensor
    spouts.append(spout.Spout(20, 6, 13))     
else:
    print("Pins described for only one spout")
    helpers.clean_exit(1)

# trap INT signal
signal.signal(signal.SIGINT, helpers.handle_signal)

# initialise randomness
random.seed()

# initialise variables we want global access to
success = False
current_spout = None
iti_broken = False
iti_break_count = 0

# record start time
p.start_time = time()
p.end_time = p.start_time + p.duration * 60
now = p.start_time

# start keeping track of performance
reward_count = 0
missed_count = 0
trial_count = 0
sponts_pins = []
sponts_t = []
reset_pins = []


## Generate config
if settings['gen_config']:
    config.gen_config(config.get_defaults(), settings['config_file'])
    helpers.clean_exit(0)


## Use utility ##
if settings['utility']:
    utils.use_util(settings, p, spouts)


## State 1 - inter-trial interval ##
def iti_break(pin):
    global iti_broken
    iti_broken = True
    global iti_break_count
    iti_break_count += 1
    global reset_pins
    reset_pins.append(pin)

def inc_sponts(pin):
    global sponts_pins
    sponts_pins.append(pin)
    global sponts_t
    sponts_t.append(time())

def iti(p, current_spout):
    is_iti = True
    global iti_broken

    # start watching for paws moving from rest position
    GPIO.add_event_detect(
            p.paw_r,
            GPIO.RISING,
            callback=iti_break,
            bouncetime=100
            )
    GPIO.add_event_detect(
            p.paw_l,
            GPIO.RISING,
            callback=iti_break,
            bouncetime=100
            )

    # start watching for spontaneous reaches to spout
    GPIO.add_event_detect(
            spouts[current_spout].touch,
            GPIO.FALLING,
            callback=inc_sponts,
            bouncetime=100
            )

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

    GPIO.remove_event_detect(p.paw_r)
    GPIO.remove_event_detect(p.paw_l)
    GPIO.remove_event_detect(spouts[current_spout].touch)
    return


## State 2 - trial period ##
def trial(p, current_spout):
    # Activate cue

    spouts[current_spout].set_cue(True)

    # Detect contact with spout
    GPIO.add_event_detect(
            spouts[current_spout].touch,
            GPIO.FALLING,
            callback=reward,
            bouncetime=p.ITI_min_ms
            )

    # Count down allowed trial time
    now = time()
    cue_end = now + p.cue_ms/1000

    # Wait until reward() is run or the trial times out
    while not success and now < cue_end:
        sleep(0.01)
        now = time()

    # Disable cue if it was a missed trial
    GPIO.output(
            spouts[current_spout].cue,
            False
            )

    # Remove spout contact detection
    GPIO.remove_event_detect(
            spouts[current_spout].touch
            )

    # Sleep in parallel with reward function, and add a second for drinking
    if success:
        sleep(p.reward_ms / 1000)   # dispensing
        sleep(1)                    # drinking

    return success


## State 3 - reward period ##
def reward(pin):
    # disable cue
    spouts[current_spout].set_cue(False)

    # set success
    global success
    success = True

    # dispense water reward
    spouts[current_spout].dispense(p.reward_ms)


## Main ##

# get past data
if settings['save_data']:
    data = helpers.request_data(settings)

print("Hit the start button to begin.")
GPIO.wait_for_edge(p.start_button, GPIO.FALLING)

while now < p.end_time:
    trial_count += 1
    success = False
    print("_________________________________")
    print("# ----- Starting trial #%i ----- #"
            % trial_count)

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


## Display results ##
resets_l      = reset_pins.count(p.paw_l)
resets_r      = reset_pins.count(p.paw_r)
print("""_________________________________

# __________ The end __________ #

Totals:
    Trials:                 %i
    Rewarded reaches:       %i (%0.1f%%)
    Missed cues:            %i (%0.1f%%)
    Spontaneous reaches:    %i
    ITI resets:             %i
        right paw:          %i
        left paw:           %i
    """ % (trial_count, reward_count, 100*reward_count/trial_count,
        missed_count, 100*missed_count/trial_count,
        len(sponts_pins), iti_break_count, resets_r, resets_l))


## Save data to disk ##
if settings['save_data']:
    # split spontaneous touches by pin
    for spout in spouts:
        sponts_pins
        sponts_t
    # TODO: format spontaneous touches for each spout

    # reformat data for saving
    # TODO: format cued touches for each spout
    # TODO: format rests for both paw rests
    # TODO: format lists for both paw rests
    data.reformat(p, spouts)

    # save data to mouse's JSON
    p.trial_count   = trial_count
    p.reward_count  = reward_count
    p.missed_count  = missed_count
    p.resets        = iti_break_count
    p.resets_l      = resets_l
    p.resets_r      = resets_r

    helpers.write_data(data, s, p)


## Finish ##
print("\nGoodbye!\n")
helpers.clean_exit(0)
