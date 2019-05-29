#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Main script
#

#TODO: perhaps actually put docstrings on things or im gonna regret 

## Libraries ##
import RPi.GPIO as GPIO
from time import sleep, time, strftime
import signal
import random
import sys
import asyncio

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
resting_l = 0
resting_r = 0

# start keeping track of performance
reward_count = 0
missed_count = 0
trial_count = 0
sponts_pins = []
sponts_t = []
resets_pins = []
resets_t = []


## Generate config
if settings['gen_config']:
    config.gen_config(config.get_defaults(), settings['config_file'])
    helpers.clean_exit(0)


## Use utility ##
if settings['utility']:
    utils.use_util(settings, p, spouts)


## State 1 - inter-trial interval ##
def set_resting_l(pin):
    global resting_l
    resting_l = 1

def set_resting_r(pin):
    global resting_r
    resting_r = 1

@asyncio.coroutine
async def lifting():
    while True:
        resting_l = resting_r = 0
        sleep(0.005)
asyncio.Task(lifting())

def iti_break(pin):
    global iti_broken
    iti_broken = True
    global iti_break_count
    iti_break_count += 1
    global resets_pins
    resets_pins.append(pin)
    global resets_t
    resets_t.append(time())

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
            callback=resting,
            bouncetime=200
            )
    GPIO.add_event_detect(
            p.paw_l,
            GPIO.RISING,
            callback=resting,
            bouncetime=200
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
    spouts[current_spout].t_cue.append(time())
    GPIO.output(spouts[current_spout].cue, True)

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
    GPIO.output(spouts[current_spout].cue, False)

    # Remove spout contact detection
    GPIO.remove_event_detect(spouts[current_spout].touch)

    # Sleep in parallel with reward function, and add a second for drinking
    if success:
        sleep(p.reward_ms / 1000)   # dispensing
        sleep(1)                    # drinking

    return success


## State 3 - reward period ##
def reward(pin):
    # disable cue
    GPIO.output(spouts[current_spout].cue, False)
    spouts[current_spout].t_touch.append(time())

    # set success
    global success
    success = True

    # dispense water reward
    spouts[current_spout].dispense(p.reward_ms)


## Main ##

# get past data
if settings['save_data']:
    data, settings['mouseID'] = helpers.request_data(settings)

# display information about current session
print("")
print("_________________________________")
print("")
print("Mouse:       %s" % settings['mouseID'])
print("Spouts:      %i" % p.spout_count)
print("Duration:    %i min" % p.duration)
print("")
print("_________________________________")
print("")

# wait to begin
print("Hit the start button to begin.")
GPIO.wait_for_edge(p.start_button, GPIO.FALLING)

# record times
p.start_time = time()
p.end_time = p.start_time + p.duration * 60
now = p.start_time

# start behaviour
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
        len(sponts_pins), iti_break_count, 
        reset_pins.count(p.paw_r), reset_pins.count(p.paw_l)))


## Save data to disk ##
if settings['save_data']:

    # spout contact
    cue = touch = release = []
    for idx, spout in enumerate(spouts):
        sponts_pins = [idx if x == spout.touch else x for x in sponts_pins]
        cue[idx] = spout.t_cue
        touch[idx] = spout.t_touch
        release[idx] = spout.t_release

    p.sponts_t = sponts_t
    p.sponts_spout = sponts_pins

    # resets
    resets_pins = ["l" if x == p.paw_l else x for x in resets_side]
    resets_pins = ["r" if x == p.paw_r else x for x in resets_side]
    p.resets_t = resets_t


    # reformat data for saving
    # TODO: format rests for both paw rests
    # TODO: format lifts for both paw rests
    data.reformat(p, spouts)

    # save data to mouse's JSON
    p.trial_count   = trial_count
    p.reward_count  = reward_count
    p.missed_count  = missed_count

    helpers.write_data(data, s, p)


## Finish ##
print("\nGoodbye!\n")
helpers.clean_exit(0)
