#!/usr/bin/env python3
""" Process settings, configuration and metadata for session

The Session class coordinates what we want to do and stores all information
about the session. This includes:
    - session settings e.g. mouse ID, configuration file used
    - configuration i.e. session, reward, cue, and ITI durations specific to
      the task
    - a raspberry pi instance that initialises and controls the pins
"""


import argparse, configparser, json, random, signal, sys, time
from os.path import isfile, join
import RPi.GPIO as GPIO

from modules.utilities import use_utility
from modules.raspberry import Pi


def parse_args():
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(
            description = 'mouse reach behavioural task sequencer'
            )

    parser.add_argument(
            '-c', '--config',
            help='Select configuration file',
            default='',
            type=str
            )

    parser.add_argument(
            '-g', '--generate_config',
            help='Generate a new configuration file',
            action='store_true'
            )

    parser.add_argument(
            '-n', '--no-data',
            help='Disable data collection',
            action='store_true'
            )

    parser.add_argument(
            '-m', '--mouseID',
            help='Specify mouseID',
            default='',
            type=str
            )

    parser.add_argument(
            '-u', '--utility',
            help='Use a utility. Pass \'list\' to list options',
            default='',
            type=str
            )

    parser.add_argument(
            '-d', '--debug',
            help='Run in debugging move',
            default='',
            action='store_true'
            )

    args = parser.parse_args()
    return args



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

        try:
            config.read(config_file)
        except configparser.MissingSectionHeaderError:
            print("%s is an invalid config file." % config_file)
            sys.exit(1)

        self.duration       =   config.getint('Settings', 'duration')
        self.spout_count    =   config.getint('Settings', 'spout_count')
        self.reward_ms      =   config.getint('Settings', 'reward_ms')
        self.cue_ms         =   config.getint('Settings', 'cue_ms')
        self.ITI_min_ms     =   config.getint('Settings', 'ITI_min_ms')
        self.ITI_max_ms     =   config.getint('Settings', 'ITI_max_ms')
        self.shaping        =   config.getboolean('Settings', 'shaping')
        json_dir            =   config.get('Settings', 'json_dir')


        # Third: initialise data handlers and hardware
        if self.save_data:
            data, self.mouseID = request_metadata(self.mouseID, json_dir)

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
            print("JSON:        %s"  % join(json_dir, self.mouseID))
        print("Spouts:      %i"     % self.spout_count)
        print("Duration:    %i min" % self.duration)
        print("Cue:         %i ms"  % self.cue_ms)
        print("ITI:         %i - %i ms" % (self.ITI_min_ms, self.ITI_max_ms))
        print("\n_________________________________\n")

        
        # Fourth: begin session
        if not self.debugging:
            print("Hit the start button to begin.")
            GPIO.wait_for_edge(self.pi.start_button, GPIO.FALLING)
            GPIO.remove_event_detect(self.pi.start_button)

        self.start_time = time.time()
        self.end_time = self.start_time + self.duration * 60
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
        self.pi.cleanup()

        # spout contact
        cue = touch = []
        for idx, spout in enumerate(self.pi.spouts):
            sponts_pins = [idx if x == spout.touch else x for x in sponts_pins]
            cue[idx] = spout.cue_t
            touch[idx] = spout.touch_t

        self.resets_pins = ["l" if x == self.pi.paw_l else x for x in self.resets_pins]
        self.resets_pins = ["r" if x == self.pi.paw_r else x for x in self.resets_pins]

        display_results((
            self.trial_count,
            self.reward_count,
            100*self.reward_count/self.trial_count,
            self.missed_count,
            100*self.missed_count/self.trial_count,
            len(self.sponts_pins),
            self.iti_break_count, 
            self.resets_pins.count("l"),
            self.resets_pins.count("r")))

        if self.save_data or self.debugging:
            print("DATA:")
            print(data)
            print("sponts_pins:")
            print(sponts_pins)
            print("resets_pins:")
            print(resets_pins)
            sys.exit(0)


            # reformat data for saving
            # TODO: format rests for both paw rests
            # TODO: format lifts for both paw rests
            data.reformat(p, spouts)

            # save data to mouse's JSON
            p.trial_count   = trial_count
            p.reward_count  = reward_count
            p.missed_count  = missed_count

            write_data(data, s, p)





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
        if not self.shaping:
            self.pi.spouts[self.current_spout].dispense(self.reward_ms)


    def iti(self):
        """ Inter-trial interval sequencer """
        is_iti = True

        # start watching for paws moving from rest position
        for paw_rest in self.pi.paw_r, self.pi.paw_l:
            GPIO.add_event_detect(
                    paw_rest,
                    GPIO.FALLING,
                    callback=self.iti_break,
                    bouncetime=20
                    )

        # start watching for spontaneous reaches to spout
        GPIO.add_event_detect(
                self.pi.spouts[self.current_spout].touch,
                GPIO.RISING,
                callback=self.inc_sponts,
                bouncetime=100
                )
        
        while is_iti:
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
                is_iti = False

        for pin in [self.pi.paw_r, self.pi.paw_l,
                self.pi.spouts[self.current_spout].touch]:
                GPIO.remove_event_detect(pin)


    def trial(self):
        """ Single trial sequencer  """
        current_spout = self.current_spout
        self.pi.spouts[current_spout].cue_t.append(time.time())
        GPIO.output(self.pi.spouts[current_spout].cue, True)
        self.pi.spouts[self.current_spout].dispense(self.reward_ms)

        # This is for the spout touch sensor
        #GPIO.add_event_detect(
        #        self.pi.spouts[current_spout].touch,
        #        GPIO.RISING,
        #        callback=reward,
        #        bouncetime=self.ITI_min_ms
        #        )

        # This is for the start button (manual cue off)
        GPIO.add_event_detect(
                self.pi.start_button,
                GPIO.FALLING,
                callback=self.reward,
                bouncetime=self.ITI_min_ms
                )

        now = time.time()
        cue_end = now + self.cue_ms/1000

        while not self.success and now < cue_end:
            time.sleep(0.010)
            now = time.time()

        GPIO.output(self.pi.spouts[current_spout].cue,
                False)

        #GPIO.remove_event_detect(
        #        self.pi.spouts[current_spout].touch
        #        )
        GPIO.remove_event_detect(
                self.pi.start_button
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
        self.iti_break_count    = random.randint(1, 100)
        self.reward_count       = random.randint(1, 100)
        self.missed_count       = random.randint(1, 100)
        self.sponts_pins        = [random.randint(1, 2)
                for x in range(random.randint(1, 100))]
        self.sponts_t           = [random.random()*1000
                for x in range(len(self.sponts_pins))].sort()
        self.resets_pins        = [random.choice([self.pi.paw_l, self.pi.paw_r])
                for x in range(random.randint(1, 100))]
        self.resets_t           = [random.random()*1000
                for x in range(len(self.resets_pins))].sort()



def default_config():
    """ Create configuration structure with default values """
    config = configparser.RawConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'duration',      '30')
    config.set('Settings', 'spout_count',   '1')
    config.set('Settings', 'reward_ms',     '300')
    config.set('Settings', 'cue_ms',        '10000')
    config.set('Settings', 'ITI_min_ms',    '4000')
    config.set('Settings', 'ITI_max_ms',    '6000')
    config.set('Settings', 'shaping',       'False')
    config.set('Settings', 'json_dir',
            '/home/pi/CuedBehaviourAnalysis/Data/TrainingJSON')

    return config



def generate_config(config, config_file):
    """ Write configuration to file  """

    if isfile(config_file):
        print("Config file %s already exists." % config_file)
        confirm = input("Overwrite? (y/N) ")
        if not confirm in ['y', 'Y']:
            sys.exit(1)
            
    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print("A new config file has been generated as %s." % config_file)



def enforce_suffix(suffix, string):
    """ Append suffix to string if not present """
    if not string.endswith(suffix):
        string = string + suffix

    return string



def request_metadata(mouseID, json_dir):
    """ Request metadata from user and load previous metadata """
    if not mouseID:
        mouseID = input("Enter mouse ID: ")

        if not mouseID:
            print("Please enter a mouse ID at the prompt or by passing -m <mouseID>")
            print("Alternatively pass -n to ignore data")
            sys.exit(1)

    date = time.strftime('%Y-%m-%d')
    data_file = join(json_dir, mouseID + '.json')
    data = {}

    if isfile(data_file):
        print("Found pre-existing training JSON for %s" % mouseID)
        with open(data_file) as json_file:
            try:
                prev_data = json.load(json_file)
                data['day'] = prev_data[-1]['day'] + 1

                prev_trainer = prev_data[-1]['trainer']
                data['trainer'] = input("Enter trainer (%s): " %
                        prev_trainer) or prev_trainer

                prev_weight = prev_data[-1]['weight']
                data['weight'] = input("Enter weight (%s): " %
                        prev_weight) or prev_weight

                prev_training_box = prev_data[-1]['box']
                data['box'] = input("Enter training box (%s): " %
                        prev_training_box) or prev_training_box
            except:
                print("Something appears to be wrong with %s" % data_file)
                sys.exit(1)

    else:
        print("This will generate a new training JSON for %s" % mouseID)
        data['day'] = 1
        data['trainer'] = input("Enter trainer: ") or 'matt'
        data['weight'] = input("Enter weight: ") or '?'
        data['box'] = input("Enter training box (1): ") or 1

    data['prewatering'] = input("Enter prewatering volume (0): ") or '0'

    return data, mouseID



def write_data(mouseID, json_dir, data):
    """ Write data to JSON file """
    data_file = join(json_dir, mouseID + '.json')

    date = time.strftime('%Y-%m-%d')
    data['date'] = date
    data['start_time'] = time.strftime('%H:%M',
            time.localtime(p.start_time)
            )
    data['spout_count'] = p.spout_count
    data['duration'] = p.duration
    data['cue_ms'] = p.cue_ms
    data['ITI_min_ms'] = p.ITI_min_ms
    data['ITI_max_ms'] = p.ITI_max_ms
    data['reward_ms'] = p.reward_ms
    data['reward_count'] = p.reward_count
    data['missed_count'] = p.missed_count
    data['trial_count'] = p.trial_count
    data['spont_count'] = p.spont_count
    data['resets_l'] = p.resets_l
    data['resets_r'] = p.resets_r

    if data['day'] == 1:
        # First day so we are not appending to existing data
        data = [data]

        with open(data_file, 'w') as output:
            json.dump(data, output, indent=4)

    else:
        # we are appending to existing data
        with open(data_file) as json_file:
            prev_data = json.load(json_file)

        prev_data.append(data)

        with open(data_file, 'w') as output:
            json.dump(prev_data, output, indent=4)

    # print out message
    print("Data was saved in:\n     %s" % data_file)


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
    left paw:           %i""" % numbers)
