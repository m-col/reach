#!/usr/bin/env python3
""" Mouse reach behavioural task sequencer """


import RPi.GPIO as GPIO
from time import sleep, time, strftime
import signal
import sys


## Setup
signal.signal(signal.SIGINT, helpers.handle_signal)

settings = helpers.parse_args(sys.argv[1:])
p = config.process_config(settings)

# pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

p.paw_r = 18
p.paw_l = 17
p.start_button = 4

GPIO.setup([p.paw_l, p.paw_r],
        GPIO.IN,
        pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(p.start_button,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP)

# create spouts
spouts = []
if p.spout_count == 1:
    # pins for cue, touch sensor, water dispensor
    spouts.append(spout.Spout(5, 22, 25))     
else:
    print("Pins described for only one spout")
    helpers.clean_exit(1)


## Generate config
if settings['gen_config']:
    config.gen_config(config.get_defaults(), settings['config_file'])
    helpers.clean_exit(0)


## Use utility ##
if settings['utility']:
    utils.use_util(settings, p, spouts)

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
