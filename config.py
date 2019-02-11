#!/usr/bin/env python3
#
# Config processor for mouse reach task control
#


## Libraries ##
import configparser, sys
from os import path


## We ultimately want to store parameters in a simple structure
class params(object):
    """ p structure holds configuration parameters """
    def __init__(self, config, config_file):
        self.session_duration = config.getint('Settings', 'session_duration')
        self.spout_count =      config.getint('Settings', 'spout_count')
        self.reward_ms =        config.getint('Settings', 'reward_ms')
        self.cue_ms =           config.getint('Settings', 'cue_ms')
        self.ITI_min =          config.getint('Settings', 'ITI_min')
        self.ITI_max =          config.getint('Settings', 'ITI_max')
        self.config_file =      config_file


## Get default settings
def get_defaults():
    config = configparser.RawConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'session_duration',  '30')
    config.set('Settings', 'spout_count',       '1')
    config.set('Settings', 'reward_ms',         '500')
    config.set('Settings', 'cue_ms',            '2000')
    config.set('Settings', 'ITI_min',           '4')
    config.set('Settings', 'ITI_max',           '6')

    return config


## Config file generator
def gen_config(config, config_file):
    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print("A new config file has been generated as %s." % config_file)


## Process config
def process_config(config_file, config_file_default):
    config = get_defaults()

    # create config file if it doesn't exist
    if not path.isfile(config_file):
        if config_file == config_file_default:
            print("No config file exists.")
            gen_config(config, config_file)
        else:
            print("Custom config file %s was not found." % config_file)
            sys.exit(1)

    # read its settings, falling back to defaults
    try:
        config.read(config_file)
    except configparser.MissingSectionHeaderError:
        print("%s is an invalid config file." % config_file)
        sys.exit(1)

    # transfer settings into p structure
    p = params(config, config_file)
    return p
