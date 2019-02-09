#!/usr/bin/env python3
#
# Config processor for mouse reach task control
#


## General settings
config_file = 'settings.ini'


## Libraries ##
import configparser
from os import path


## We ultimately want to store parameters in a simple structure
class params(object):
    """ p structure holds configuration parameters """
    def __init__(self, config):
        self.session_duration = config.getint('Settings', 'session_duration')
        self.spout_count = config.getint('Settings', 'spout_count')
        self.reward_ms = config.getint('Settings', 'reward_ms')
        self.ITI_min = config.getint('Settings', 'ITI_min')
        self.ITI_max = config.getint('Settings', 'ITI_max')


## Get default settings
def get_defaults():
    config = configparser.RawConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'session_duration',  '30')
    config.set('Settings', 'spout_count',       '1')
    config.set('Settings', 'reward_ms',         '500')
    config.set('Settings', 'ITI_min',           '4')
    config.set('Settings', 'ITI_max',           '6')
    return config


## Config file generator
def gen_config(config):
    print("No config file exists.")
    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print("A new config file has been generated as %s." % config_file)


## Process config
def process_config():
    config = get_defaults()
    
    # create config file if it doesn't exist
    if not path.isfile(config_file):
        gen_config(config)
    
    # read its settings, falling back to defaults
    config.read(config_file)

    # transfer settings into p structure
    p = params(config)
    return p
