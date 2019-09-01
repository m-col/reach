#!/usr/bin/env python3
""" Process settings, configuration and metadata for session

The Session class coordinates what we want to do and stores all information
about the session. This includes:
    - session settings e.g. mouse ID, configuration file used
    - configuration i.e. session, reward, cue, and ITI durations specific to
      the task
    - a raspberry pi instance that initialises and controls the pins
"""

# pylint: disable=import-error, unused-argument, fixme

from os.path import isfile, join
import random
import signal
import sys
import time

from reach.utilities import use_utility
from reach.raspberry import Pi
import reach.io as io


random.seed()


def _exit(signum, frame):
    """ Simple exitting signal handler for Ctrl-C events before raspberry pins
    are initialised """
    if signum == 2:
        sys.exit(1)


class Session():
    """ This structure stores all behavioural settings and session metadata """

    signal.signal(
        signal.SIGINT,
        _exit
    )

    def __init__(self):
        """ Process initial settings from args and config file """

        # First: parse arguments to decide what to do
        args = io.parse_args()

        # TODO: move this entire args chunk out of Session

        if args.config:
            config_file = io.enforce_suffix('.ini', args.config)
        else:
            config_file = 'settings.ini'

        if args.utility:
            use_utility(args.utility)

        if args.generate_config:
            io.generate_config(config_file)
            sys.exit(0)

        # Second: configure settings for session
        if not isfile(config_file):
            if config_file == 'settings.ini':
                print("No config file exists.")
                io.generate_config(config_file)
            else:
                print("Custom config file %s was not found." % config_file)
                sys.exit(1)

        params = io.read_config(config_file)
        params['mouse_id'] = args.mouse_id
        params['save_data'] = not args.no_data

        # Third: initialise data handlers and hardware
        if params['save_data']:
            self.data, params['mouse_id'] = io.request_metadata(
                params['mouse_id'], params['json_dir'])

        # TODO: move most of these into dedicated data dict
        self.water_at_cue_onset = params['shaping']
        self.success = False
        self.current_spout = None
        self.iti_broken = False
        self.iti_break_count = 0
        # TODO: remove all 'count' variables completely; only used for printing
        # results at the end and we can count the data
        self.reward_count = 0
        self.missed_count = 0
        self.trial_count = 0
        self.sponts_pins = []
        self.sponts_t = []
        self.resets_pins = []
        self.resets_t = []
        self.params = params
        self.rpi = Pi(params['spout_count'])

        print("\n_________________________________\n")
        if params['save_data']:
            print("Mouse:       %s" % params['mouse_id'])
            print("JSON:        %s" %
                  join(params['json_dir'], params['mouse_id']))
        print("Spouts:      %i" % params['spout_count'])
        print("Duration:    %i min" % params['duration'])
        print("Cue:         %i ms" % params['cue_ms'])
        print("ITI:         %i - %i ms" % params['iti'])
        print("Shaping:     %s" % params['shaping'])
        print("\n_________________________________\n")

        # Fourth: begin session
        self.rpi.wait_to_start()

        if params['save_data']:
            signal.signal(
                signal.SIGINT,
                self.cleanup_with_prompt
            )

        now = time.time()
        params['start_time'] = now
        params['end_time'] = now + params['duration']

        while now < params['end_time']:
            self.trial_count += 1
            self.success = False
            print("_________________________________________")
            print("# ---- Starting trial #%i -- %4.0f s ---- #"
                  % (self.trial_count, now - params['start_time']))

            self.current_spout = random.randint(0, params['spout_count'] - 1)
            self.iti()
            self.trial()

            print("Total rewards: %i" % self.reward_count)
            now = time.time()

        # Fifth: end session
        self.collate_data()
        display_results((  # TODO: replace with something not hideous
            self.trial_count,
            self.reward_count,
            100 * self.reward_count / self.trial_count,
            self.missed_count,
            100 * self.missed_count / self.trial_count,
            len(self.sponts_pins),
            self.iti_break_count,
            self.data['resets_sides'].count("l"),
            self.data['resets_sides'].count("r"),
            self.reward_count,
            self.reward_count * 6
        ))

        if self.params['save_data']:
            notes = input("\nAdd any notes to save (empty adds none):\n")
            if notes:
                self.data["notes"] = notes
            io.write_data(params['mouse_id'], params['json_dir'], self.data,
                          append_last_entry=args.append)

        self.rpi.cleanup()
        print('\a')

    def iti_break(self, pin):
        """ Callback when the ITI is broken by premature movement """
        self.iti_broken = True
        self.iti_break_count += 1
        self.resets_pins.append(pin)
        self.resets_t.append(time.time())

    def inc_sponts(self, pin):
        """ Callback upon spontaneous reach """
        self.sponts_pins.append(pin)
        self.sponts_t.append(time.time())

    def reward(self, pin):
        """ Callback for rewarding cued reach """
        self.rpi.successful_grasp(self.current_spout)
        self.success = True
        if not self.water_at_cue_onset:
            self.rpi.dispense(self.current_spout,
                              self.params['reward_ms'])

    def iti(self):
        """ Inter-trial interval sequencer """

        self.rpi.monitor_sensors(
            self.current_spout,
            self.iti_break,
            self.inc_sponts
        )

        # button press reverses shaping boolean for next trial
        self.rpi.reset_button_callback(self.reverse_shaping)
        self.water_at_cue_onset = self.params['shaping']

        while True:
            self.rpi.wait_for_rest()
            self.iti_broken = False
            iti_duration = random.uniform(*self.params['iti']) / 1000
            print("Counting down %.2fs" % iti_duration)
            now = time.time()
            trial_start = now
            trial_end = trial_start + iti_duration

            while now < trial_end and not self.iti_broken:
                time.sleep(0.02)
                now = time.time()

            if self.iti_broken:
                continue
            else:
                break

        self.rpi.disable_sensors(self.current_spout)

    def trial(self):
        """ Single trial sequencer """
        current_spout = self.current_spout
        self.rpi.start_trial(current_spout, self.reward)

        if self.water_at_cue_onset:
            self.rpi.dispense(current_spout, self.params['reward_ms'])

        now = time.time()
        cue_end = now + self.params['cue_ms'] / 1000

        while not self.success and now < cue_end:
            time.sleep(0.008)
            now = time.time()

        self.rpi.end_trial(current_spout)

        # Sleep in parallel with reward function, adding a second for drinking
        if self.success:
            print("Successful reach!")
            self.reward_count += 1
            time.sleep(self.params['reward_ms'] / 1000 + 1)
        else:
            print("Missed reach")
            self.missed_count += 1

    def collate_data(self, interrupted=False):
        """ Organise all metadata and collected data into single structure """

        # TODO: completely rewrite this method
        params = self.params
        if interrupted:
            # This was called via Control-C callback
            params['end_time'] = time.time()
            params['duration'] = params['end_time'] - params['start_time']

        cue_t = []
        touch_t = []
        for idx, spout in enumerate(self.rpi.spouts):
            self.sponts_pins = [
                idx if x == spout['touch'] else x for x in self.sponts_pins
            ]
            cue_t.append(spout['cue_t'])
            touch_t.append(spout['touch_t'])

        # TODO: can this be written more nicely?
        self.resets_pins = [
            "l" if x == self.rpi.paws[0] else x for x in self.resets_pins
        ]
        self.resets_pins = [
            "r" if x == self.rpi.paws[1] else x for x in self.resets_pins
        ]

        if not params['save_data']:
            self.data = {}
        data = self.data

        # session parameters
        data['date'] = time.strftime('%Y-%m-%d')
        data['start_time'] = time.strftime(
            '%H:%M:%S', time.localtime(self.params['start_time'])
        )
        data['end_time'] = time.strftime(
            '%H:%M:%S',
            time.localtime(params['end_time'])
        )
        data['spout_count'] = params['spout_count']
        data['duration'] = params['duration']
        data['cue_ms'] = params['cue_ms']
        data['iti'] = params['iti']
        data['reward_ms'] = params['reward_ms']
        data['shaping'] = params['shaping']

        # behavioural data
        data['trial_count'] = self.trial_count
        data['reward_count'] = self.reward_count
        data['missed_count'] = self.missed_count
        data['sponts_pins'] = self.sponts_pins
        data['iti_break_count'] = self.iti_break_count
        data['resets_sides'] = self.resets_pins
        data['resets_t'] = self.resets_t
        data['cue_t'] = cue_t
        data['touch_t'] = touch_t

    def reverse_shaping(self, pin):
        """ Callback to make next trial reverse shaping boolean
        i.e. switch dispensing of water between cue onset and grasp """
        self.water_at_cue_onset = not self.water_at_cue_onset
        print("For next trial, water at cue onset = %s"
              % self.water_at_cue_onset)
        # TODO: fix erroneous reverse_shaping at start of session

    def cleanup_with_prompt(self, signum, frame):
        """ Control-C signal handler covering main training period

        This will prompt to save data collected thus far before
        uninitialising the raspberry pi and exiting """

        response = input(
            "\nExiting: Do you want to keep collected data? (N/y) "
        )
        if response == "y":
            self.collate_data(True)
            notes = input("\nAdd any notes to save (empty adds none):\n")
            if notes:
                self.data["notes"] = notes
            io.write_data(
                self.params['mouse_id'], self.params['json_dir'], self.data
            )

        self.rpi.cleanup()


def display_results(numbers):
    """ Print results at the end of the session """
    print("""_________________________________

# __________ The end __________ #

Trials:                 %i
Rewarded reaches:       %i (%0.1f%%)
Missed cues:            %i (%0.1f%%)
Spontaneous reaches:    %i
ITI resets:             %i
    right paw:          %i
    left paw:           %i
# _____________________________ #

%i rewards * 6uL = %i uL
    """ % numbers)
