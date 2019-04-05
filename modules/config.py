#!/usr/bin/env python3
#
# Mouse reach task sequencer
#       Configuration processor
#


## Libraries ##
import configparser, sys
from os import path

from modules.helpers import clean_exit


## We ultimately want to store parameters in a simple structure
class params(object):
    """ p structure holds configuration parameters """
    def __init__(self, config):
        self.duration =         config.getint('Settings', 'duration')
        self.spout_count =      config.getint('Settings', 'spout_count')
        self.reward_ms =        config.getint('Settings', 'reward_ms')
        self.cue_ms =           config.getint('Settings', 'cue_ms')
        self.ITI_min_ms =       config.getint('Settings', 'ITI_min_ms')
        self.ITI_max_ms =       config.getint('Settings', 'ITI_max_ms')


## Get default settings
def get_defaults():
    config = configparser.RawConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'duration',      '30')
    config.set('Settings', 'spout_count',   '1')
    config.set('Settings', 'reward_ms',     '300')
    config.set('Settings', 'cue_ms',        '10000')
    config.set('Settings', 'ITI_min_ms',    '4000')
    config.set('Settings', 'ITI_max_ms',    '6000')

    return config


## Config file generator
def gen_config(config, config_file):

    if path.isfile(config_file):
        confirm = input("Config file %s already exists. Overwrite? (Y/n) "
                % config_file)
        if confirm == "n":
            clean_exit(1)
            
    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print("A new config file has been generated as %s." % config_file)


## Process config
def process_config(settings):
    config = get_defaults()

    # create config file if it doesn't exist
    if not path.isfile(settings['config_file']):
        if settings['custom_config']:
            print("Custom config file %s was not found." % settings['config_file'])
            clean_exit(1)
        else:
            print("No config file exists.")
            gen_config(config, settings['config_file'])

    # read its settings, overwriting defaults with any specified settings
    try:
        config.read(settings['config_file'])
    except configparser.MissingSectionHeaderError:
        print("%s is an invalid config file." % settings['config_file'])
        clean_exit(1)

    # generate parameter structure
    p = params(config)
    return p
