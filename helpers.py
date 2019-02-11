#!/usr/bin/env python3
#
# Helper functions for mouse reach task control
#


## Libraries ##
import RPi.GPIO as GPIO
import sys
import getopt

# custome
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


## Signal handler ##
def handle_signal(sig, frame):
    if sig == 2:
        GPIO.cleanup()
        sys.exit()


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
