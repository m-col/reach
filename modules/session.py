#!/usr/bin/env python3
""" Control the ongoing session and record its data """

import random

class Pins:
    

class Session:
    """ A reach task session """

    def __init__(self):
        random.seed()

        self.success = False
        self.current_spout = None
        self.iti_broken = False
        self.iti_break_count = 0

        self.reward_count = 0
        self.missed_count = 0
        self.trial_count = 0
        self.sponts_pins = []
        self.sponts_t = []
        self.resets_pins = []
        self.resets_t = []

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
    for paw_rest in p.paw_r, p.paw_l:
        GPIO.add_event_detect(
                paw_rest,
                GPIO.FALLING,
                callback=iti_break,
                bouncetime=20
                )

    # start watching for spontaneous reaches to spout
    GPIO.add_event_detect(
            spouts[current_spout].touch,
            GPIO.RISING,
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


def reward(pin):
    # disable cue
    GPIO.output(spouts[current_spout].cue, False)
    spouts[current_spout].t_touch.append(time())

    # set success
    global success
    success = True

    # dispense water reward
    spouts[current_spout].dispense(p.reward_ms)

