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

# external
import external.gertbot as gertbot


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
        -n              run but do not save metadata
        -m <mouseID>    specify mouseID for this run
        -u <utility>    use utility and exit. Pass 'list' to list utilities
    """
    print(help_msg)


## Parse command line arguments ##
def parse_args(argv):
    """ Parse command line arguments to create settings dict """

    # default settings
    settings = {
            'save_metadata': True, 
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

        elif opt == '-n':       # flag to not save metadata
            settings['save_metadata'] = False

        elif opt == '-m':
            settings['mouseID'] = arg

        elif opt == '-u':       # use a utility
            settings['utility'] = arg
            settings['save_metadata'] = False

    return settings


## Clean up pins and exit
def clean_exit(exit_code):
    """ Clean up allocation of GPIO pins """
    GPIO.output(24, False)  # close solenoid
    GPIO.cleanup()
    gertbot.stop_all()
    sys.exit(exit_code)


## Signal handler ##
def handle_signal(sig, frame):
    """ Run clean_exit upon ctrl-c """
    if sig == 2:
        clean_exit(1)


## Request metadata ##
def request_metadata(settings):
    """ Get metadata from a mouse JSON file """

    if not settings['mouseID']:
        settings['mouseID'] = input("Enter mouse ID: ")
    mouseID = settings['mouseID']

    if not mouseID:
        print("Please enter a mouse ID at the prompt or by passing -m <mouseID>")
        print("Alternatively pass -n to ignore metadata")
        clean_exit(1)

    date = time.strftime('%Y-%m-%d')
    metadata_file = mouseID + '.json'
    metadata = {}

    if path.isfile(metadata_file):
        # load metadata from pre-existing training JSON
        print("Found pre-existing training JSON for %s" % mouseID)
        with open(metadata_file) as json_file:
            try:
                prev_metadata = json.load(json_file)
                metadata['day'] = prev_metadata[-1]['day'] + 1

                prev_trainer = prev_metadata[-1]['trainer']
                metadata['trainer'] = input("Enter trainer (%s): " %
                        prev_trainer) or prev_trainer

                prev_weight = prev_metadata[-1]['weight']
                metadata['weight'] = input("Enter weight (%s): " %
                        prev_weight) or prev_weight

                prev_training_box = prev_metadata[-1]['box']
                metadata['box'] = input("Enter training box (%s): " %
                        prev_training_box) or prev_training_box
            except:
                print("Something appears to be wrong with %s" % metadata_file)
                sys.exit(1)

    else:
        # we will save to new training JSON
        print("Generating new training JSON for %s" % mouseID)
        metadata['day'] = 1
        metadata['trainer'] = input("Enter trainer: ") or 'matt'
        metadata['weight'] = input("Enter weight: ") or '?'
        metadata['box'] = input("Enter training box: ") or 1

    metadata['prewatering'] = input("Enter prewatering volume (0): ") or '0'

    return metadata, mouseID


## Save metadata ##
def write_metadata(metadata, settings, p):
    """ Write metadata to a mouse JSON file """
    metadata_file = settings['mouseID'] + '.json'

    date = time.strftime('%Y-%m-%d')
    metadata['date'] = date
    metadata['start_time'] = time.strftime('%H:%M',
            time.localtime(p.start_time))
    metadata['data_file'] = date + '_' + mouseID
    metadata['spout_count'] = p.spout_count
    metadata['duration'] = p.duration
    metadata['cue_ms'] = p.cue_ms
    metadata['ITI_min_ms'] = p.ITI_min_ms
    metadata['ITI_max_ms'] = p.ITI_max_ms
    metadata['reward_ms'] = p.reward_ms
    metadata['reward_count'] = p.reward_count
    metadata['missed_count'] = p.missed_count
    metadata['trial_count'] = p.trial_count
    metadata['spont_count'] = p.spont_count
    metadata['resets_l'] = p.resets_l
    metadata['resets_r'] = p.resets_r

    if metadata['day'] == 1:
        # First day so we are not appending to existing metadata
        metadata = [metadata]

        with open(metadata_file, 'w') as output:
            json.dump(metadata, output, indent=4)

    else:
        # we are appending to existing metadata
        with open(metadata_file) as json_file:
            prev_metadata = json.load(json_file)

        prev_metadata.append(metadata)

        with open(metadata_file, 'w') as output:
            json.dump(prev_metadata, output, indent=4)

    # print out message
    print("Metadata was saved in:\n     %s" % metadata_file)


## Keep track of behavioural data ##
class Data(object):
    """ Store and manipulate behavioural data during training session """

    def __init__(self):
        """ Initialise data structure """
        self.lift_l     = []
        self.lift_r     = []
        self.rest_l     = []
        self.rest_r     = []
        self.grab       = []
        self.release    = []
        self.cue        = []

    def reaction_time(self, time):
        self.reaction_times.append(time)



## Enforce suffix ##
def enforce_suffix(suffix, string):
    """ Append suffix to string if not present """
    if not string.endswith(suffix):
        string = string + suffix

    return string
