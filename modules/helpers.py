#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Helper functions
#


## Libraries ##
import RPi.GPIO as GPIO
import sys
import getopt
import json
import time
from os import path


## Print help ##
def print_help():
    """ Display help information """
    help_msg = """
        Mouse reach task sequencer
        Usage: ./main.py [OPTIONS]

        Options:
        -h              print this help message and exit
        -c              specify non-default config file and run
        -g              generate default config file and exit
        -n              run but do not save data
        -N              run but do not save training data
        -m <mouseID>    specify mouseID for this run
        -u <utility>    use utility and exit. Pass 'list' to list utilities
    """
    print(help_msg)


## Parse command line arguments ##
def parse_args(argv):
    """ Parse command line arguments to create settings dict """

    # default settings
    settings = {
            'save_data': True, 
            'utility': '',
            'config_file': 'settings.ini',
            'custom_config': False,
            'mouseID': '',
            'gen_config': False,
            }

    to_gen_config = False

    try:
        opts, args = getopt.getopt(argv, 'hc:gnm:u:')
    except getopt.GetoptError:
        print("Error parsing arguments. Pass -h for help.")
        sys.exit(1)

    for opt, arg in opts:

        if opt == '-h':         # print help and exit
            print_help()
            sys.exit(0)

        elif opt == '-c':       # specify config file
            settings['config_file'] = enforce_suffix('.ini', arg)
            settings['custom_config'] = True

        elif opt == '-g':       # generate config file and exit
            settings['gen_config'] = True

        elif opt == '-n':       # flag to not save data
            settings['save_data'] = False

        elif opt == '-m':
            settings['mouseID'] = arg

        elif opt == '-u':       # use a utility
            settings['utility'] = arg
            settings['save_data'] = False

    return settings


## Clean up pins and exit
def clean_exit(exit_code):
    """ Clean up allocation of GPIO pins """
    GPIO.output(24, False)  # close solenoid
    GPIO.cleanup()
    sys.exit(exit_code)


## Signal handler ##
def handle_signal(sig, frame):
    """ Run clean_exit upon ctrl-c """
    if sig == 2:
        clean_exit(1)


## Request past data ##
def request_data(settings):
    """ Get data from mouse JSON file """

    if not settings['mouseID']:
        settings['mouseID'] = input("Enter mouse ID: ")
    mouseID = settings['mouseID']

    if not mouseID:
        print("Please enter a mouse ID at the prompt or by passing -m <mouseID>")
        print("Alternatively pass -n to ignore data")
        clean_exit(1)

    date = time.strftime('%Y-%m-%d')
    data_file = mouseID + '.json'
    data = {}

    if path.isfile(data_file):
        # load data from pre-existing training JSON
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
                clean_exit(1)

    else:
        # save to new JSON
        print("Generating new training JSON for %s" % mouseID)
        data['day'] = 1
        data['trainer'] = input("Enter trainer: ") or 'matt'
        data['weight'] = input("Enter weight: ") or '?'
        data['box'] = input("Enter training box: ") or 1

    data['prewatering'] = input("Enter prewatering volume (0): ") or '0'

    return data, mouseID


## Save data ##
def write_data(data, settings, p):
    """ Write data to a mouse JSON file """
    data_file = settings['mouseID'] + '.json'

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


## Keep track of behavioural data ##
class Data(object):
    """ Store and manipulate behavioural data during training session """

    def __init__(self, spouts):
        """ Initialise data structure """
        # paw rest touch sensors
        self.lift       = []
        self.rest       = []
        self.grab       = []
        self.release    = []

    def reformat(self, p, spouts, sponts):
        """ Re-format the data for saving """
        # get data from each spout
        cue = []
        touch = []
        release = []
        for i in range(len(spouts)):
            cue.append(spouts[i].t_cue)
            touch.append(spouts[i].t_touch)
            release.append(spouts[i].t_release)

        self.cue = cue
        self.touch = touch
        self.release = release

        # get paw sensor data
        lift_l
        lift_r
        rest_l
        rest_r


## Enforce suffix ##
def enforce_suffix(suffix, string):
    """ Append suffix to string if not present """
    if not string.endswith(suffix):
        string = string + suffix

    return string
