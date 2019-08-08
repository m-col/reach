#!/usr/bin/env python3
""" Process settings, configuration and metadata for session

The Session class coordinates what we want to do and stores all information
about the session. This includes:
    - session settings e.g. mouse ID, configuration file used
    - configuration i.e. session, reward, cue, and ITI durations specific to
      the task
    - a raspberry pi instance that initialises and controls the pins
"""


from reach.utilities import use_utility
from reach.raspberry import Pi
from reach.io import *
import json, random, signal, sys, time
from os.path import isfile, join

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import PPi.GPIO as GPIO



def exit(signum, frame):
    """ Simple exitting signal handler for Ctrl-C events before raspberry pins
    are initialised """
    if signum == 2:
        sys.exit(1)



class Session(object):
    """ This structure stores all behavioural settings and session metadata """

    signal.signal(
            signal.SIGINT,
            exit
            )

    def __init__(self):
        """ Process initial settings from args and config file """

        # First: parse arguments to decide what to do
        args = parse_args()

        self.save_data = not args.no_data
        self.mouseID = args.mouseID
        self.debugging = args.debug

        if args.config:
            self.config_file = enforce_suffix('.ini', args.config)
        else:
            self.config_file = 'settings.ini'
        config_file = self.config_file

        if args.utility:
            use_utility(args.utility)

        if args.generate_config:
            generate_config(default_config(), config_file)
            sys.exit(0)


        # Second: configure settings for session
        config = default_config()

        if not isfile(config_file):
            if config_file is 'settings.ini':
                print("No config file exists.")
                generate_config(config, config_file)
            else:
                print("Custom config file %s was not found." % config_file)
                sys.exit(1)

        config = read_config(config, config_file)

        self.duration       =   config.getint('Settings', 'duration')
        self.spout_count    =   config.getint('Settings', 'spout_count')
        self.reward_ms      =   config.getint('Settings', 'reward_ms')
        self.cue_ms         =   config.getint('Settings', 'cue_ms')
        self.ITI_min_ms     =   config.getint('Settings', 'ITI_min_ms')
        self.ITI_max_ms     =   config.getint('Settings', 'ITI_max_ms')
        self.shaping        =   config.getboolean('Settings', 'shaping')
        self.json_dir       =   config.get('Settings', 'json_dir')


        # Third: initialise data handlers and hardware
        if self.save_data:
            self.data, self.mouseID = request_metadata(self.mouseID, self.json_dir)
                    
        self.success            = False
        self.current_spout      = None
        self.iti_broken         = False
        self.iti_break_count    = 0
        self.reward_count       = 0
        self.missed_count       = 0
        self.trial_count        = 0
        self.sponts_pins        = []
        self.sponts_t           = []
        self.resets_pins        = []
        self.resets_t           = []

        random.seed()
        self.pi = Pi(self.spout_count)

        print("\n_________________________________\n")
        if self.save_data:
            print("Mouse:       %s"     % self.mouseID)
            print("JSON:        %s"  % join(self.json_dir, self.mouseID))
        print("Spouts:      %i"     % self.spout_count)
        print("Duration:    %i min" % self.duration)
        print("Cue:         %i ms"  % self.cue_ms)
        print("ITI:         %i - %i ms" % (self.ITI_min_ms, self.ITI_max_ms))
        print("Shaping:     %s" % self.shaping)
        print("\n_________________________________\n")

        
        # Fourth: begin session
        if not self.debugging:
            print("Hit the start button to begin.")
            GPIO.wait_for_edge(self.pi.start_button, GPIO.FALLING)

        if self.save_data:
            signal.signal(
                    signal.SIGINT,
                    self.cleanup_with_prompt
                    )

        self.start_time = time.time()
        self.end_time = self.start_time + self.duration
        now = self.start_time

        if self.debugging:
            self.end_time = now - 1
            self.randomise_data()


        while now < self.end_time:
            self.trial_count += 1
            self.success = False
            print("_________________________________")
            print("# ----- Starting trial #%i ----- #"
                    % self.trial_count)

            self.current_spout = random.randint(0, self.spout_count - 1)
            self.iti()
            self.trial()

            print("Total rewards: %i" % self.reward_count)
            now = time.time()


        # Fifth: end session
        data = self.collate_data(False)
        display_results((
            self.trial_count,
            self.reward_count,
            100*self.reward_count/self.trial_count,
            self.missed_count,
            100*self.missed_count/self.trial_count,
            len(self.sponts_pins),
            self.iti_break_count, 
            self.data['resets_sides'].count("l"),
            self.data['resets_sides'].count("r")))

        if self.save_data:
            notes = input("\nAdd any notes to save (empty adds none):\n")
            if notes:
                data["notes"] = notes
            write_data(self.mouseID, self.json_dir, data)

        self.pi.cleanup()


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
        GPIO.output(self.pi.spouts[self.current_spout].cue, False)
        self.pi.spouts[self.current_spout].touch_t.append(time.time())
        self.success = True
        if not self.water_at_cue_onset:
            self.pi.spouts[self.current_spout].dispense(self.reward_ms)


    def iti(self):
        """ Inter-trial interval sequencer """

        # start watching for paws moving from rest position
        for paw_rest in self.pi.paw_r, self.pi.paw_l:
            GPIO.add_event_detect(
                    paw_rest,
                    GPIO.FALLING,
                    callback=self.iti_break,
                    bouncetime=40
                    )

        # start watching for spontaneous reaches to spout
        GPIO.add_event_detect(
                self.pi.spouts[self.current_spout].touch,
                GPIO.RISING,
                callback=self.inc_sponts,
                bouncetime=100
                )

        # button press reverses shaping boolean for next trial
        GPIO.remove_event_detect(self.pi.start_button)
        self.water_at_cue_onset = True if self.shaping else False
        GPIO.add_event_detect(
                self.pi.start_button,
                GPIO.FALLING,
                callback=self.reverse_shaping,
                bouncetime=500
                )

        while True:
            print("Waiting for rest...")
            while not all([GPIO.input(self.pi.paw_l),
                    GPIO.input(self.pi.paw_r)]):
                time.sleep(0.010)

            self.iti_broken = False
            ITI_duration = random.uniform(self.ITI_min_ms, self.ITI_max_ms) / 1000
            print("Counting down %.2fs" % ITI_duration)
            now = time.time()
            trial_start = now
            trial_end = trial_start + ITI_duration

            while now < trial_end and not self.iti_broken:
                time.sleep(0.02)
                now = time.time()

            if self.iti_broken:
                continue
            else:
                break

        for pin in [self.pi.paw_r, self.pi.paw_l,
                self.pi.spouts[self.current_spout].touch]:
                GPIO.remove_event_detect(pin)


    def trial(self):
        """ Single trial sequencer """
        current_spout = self.current_spout
        self.pi.spouts[current_spout].cue_t.append(time.time())
        GPIO.output(self.pi.spouts[current_spout].cue, True)
        if self.water_at_cue_onset:
            self.pi.spouts[self.current_spout].dispense(self.reward_ms)

        GPIO.add_event_detect(
                self.pi.spouts[current_spout].touch,
                GPIO.RISING,
                callback=self.reward,
                bouncetime=1000
                )

        now = time.time()
        cue_end = now + self.cue_ms/1000

        while not self.success and now < cue_end:
            time.sleep(0.010)
            now = time.time()

        GPIO.output(self.pi.spouts[current_spout].cue,
                False)

        GPIO.remove_event_detect(
                self.pi.spouts[current_spout].touch
                )

        # Sleep in parallel with reward function, and add a second for drinking
        if self.success:
            print("Successful reach!")
            self.reward_count += 1
            time.sleep(self.reward_ms / 1000 + 1) 
        else:
            print("Missed reach")
            self.missed_count += 1


    def randomise_data(self):
        """ Create random data in all data variables """
        self.iti_break_count    = random.randint(1, 10)
        self.reward_count       = random.randint(1, 10)
        self.missed_count       = random.randint(1, 10)
        self.trial_count        = self.reward_count + self.missed_count
        self.sponts_pins        = [random.randint(1, 2)
                for x in range(random.randint(1, 10))]
        self.sponts_t           = [random.random()*1000
                for x in range(len(self.sponts_pins))].sort()
        self.resets_pins        = [random.choice([self.pi.paw_l, self.pi.paw_r])
                for x in range(random.randint(1, 10))]
        self.resets_t           = [int(random.random()*1000)
                for x in range(len(self.resets_pins))]
        self.resets_t.sort()


    def collate_data(self, interrupted):
        """ Organise all metadata and collected data into single structure """

        if interrupted:
            # This was called via Control-C callback
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

        cue_t = []
        touch_t = []
        for idx, spout in enumerate(self.pi.spouts):
            self.sponts_pins = [idx if x == spout.touch else x for x in self.sponts_pins]
            cue_t.append(spout.cue_t)
            touch_t.append(spout.touch_t)

        self.resets_pins = ["l" if x == self.pi.paw_l else x for x in self.resets_pins]
        self.resets_pins = ["r" if x == self.pi.paw_r else x for x in self.resets_pins]

        # session parameters
        data = self.data
        data['date'] = time.strftime('%Y-%m-%d')
        data['start_time'] = time.strftime('%H:%M:%S',
                time.localtime(self.start_time)
                )
        data['end_time'] = time.strftime('%H:%M:%S',
                time.localtime(self.end_time)
                )
        data['spout_count']     = self.spout_count
        data['duration']        = self.duration
        data['cue_ms']          = self.cue_ms
        data['ITI_min_ms']      = self.ITI_min_ms
        data['ITI_max_ms']      = self.ITI_max_ms
        data['reward_ms']       = self.reward_ms
        data['shaping']         = self.shaping

        # behavioural data
        data['trial_count']     = self.trial_count
        data['reward_count']    = self.reward_count
        data['missed_count']    = self.missed_count
        data['sponts_pins']     = self.sponts_pins
        data['iti_break_count'] = self.iti_break_count
        data['resets_sides']    = self.resets_pins
        data['resets_t']        = self.resets_t
        data['cue_t']           = cue_t
        data['touch_t']         = touch_t
        return data
    

    def reverse_shaping(self, pin):
        """ Callback to make next trial reverse shaping boolean
        i.e. switch dispensing of water between cue onset and grasp """
        self.water_at_cue_onset = False if self.water_at_cue_onset else True
        print("For next trial, water at cue onset = %s" % self.water_at_cue_onset)


    def cleanup_with_prompt(self, signum, frame):
        """ Control-C signal handler covering main training period

        This will prompt to save data collected thus far before
        uninitialising the raspberry pi and exiting """
        
        response = input("\nExiting: Do you want to keep collected data? (N/y) ") 
        if response is "y":
            data = self.collate_data(True)
            notes = input("\nAdd any notes to save (empty adds none):\n")
            if notes:
                data["notes"] = notes
            write_data(self.mouseID, self.json_dir, data)

        self.pi.cleanup()



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
    """ % numbers)
