#!/usr/bin/env python3
#
# Helper functions for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO
import sys
import getopt
import json
import time
from os import path

# custom
import config

## Print help
def print_help():
    help_msg = """
        Mouse reach task sequencer
        Usage: ./main.py [OPTIONS]

        Options:
        -h          print this help message and exit
        -c          specify non-default config file and run
        -g          generate default config file and exit
        -n          run but do not save metadata
    """
    print(help_msg)


## Parse command line arguments
def parse_args(argv, config_file):
    # some defaults
    save_metadata = True

    try:
        opts, args = getopt.getopt(argv, 'hc:gn')
    except getopt.GetoptError:
        print("Error parsing arguments. Pass -h for help.")
        sys.exit(1)

    for opt, arg in opts:

        if opt == '-h':         # print help and exit
            print_help()
            sys.exit(0)

        elif opt == '-c':       # specify config file
            config_file = arg

        elif opt == '-g':       # generate config file and exit
            config.gen_config(config.get_defaults(), config_file)
            sys.exit(0)

        elif opt == '-n':       # flag to not save metadata
            save_metadata = False

    return config_file, save_metadata
## Signal handler ##
def handle_signal(sig, frame):
    if sig == 2:
        GPIO.cleanup()
        sys.exit()


## Request metadata ##
def request_metadata():
    mouseID = input("Enter mouse ID: ")
    if not mouseID:
        print("Please enter a mouse ID or pass -n to ignore metadata")
        sys.exit(1)

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
def write_metadata(metadata, mouseID, p):
    metadata_file = mouseID + '.json'

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
