"""
Training Configuration files
============================

Config files handle training session configuration through config files.

"""


import configparser
import json
import sys
from os.path import isfile

from reach.utilities import enforce_suffix


def _default_config():
    """
    Create config parser object with default values.
    """
    config = configparser.RawConfigParser()

    config.add_section('Settings')
    config.set('Settings', 'duration', 2400)
    config.set('Settings', 'spout_count', 1)
    config.set('Settings', 'reward_duration_ms', '[100, 100]')
    config.set('Settings', 'iti', '[4000, 6000]')
    config.set('Settings', 'json_path',
               '/home/pi/CuedBehaviourAnalysis/Data/TrainingJSON')

    return config


def _write_config(config_file, config=None):
    """
    Write configuration to file.

    Parameters
    ----------
    config_file : string
        Path to file where config will be stored.

    config : optional
        The configuration settings that will be stored. Default settings will
        be stored if this is not given.

    """

    if isfile(config_file):
        print(f"Config file {config_file} already exists.")
        confirm = input('Overwrite? (y/N) ')
        if confirm not in ['y', 'Y']:
            print('Cancelled')
            sys.exit(1)

    if config is None:
        config = _default_config()

    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print(f"A new config file has been generated as {config_file}.")


def read_config(config_file):
    """
    Read settings from config file and return as dict.

    Parameters
    ----------
    config_file : string or None
        Path to configuration file containing training settings. Alternatively
        this can be None, which will make us use default settings.

    """
    config = _default_config()

    if config_file is not None:
        config_file = enforce_suffix(config_file, '.ini')

        if not isfile(config_file):
            print(f"{config_file} config file does not exist.")
            response = input("Generate a new one? [Y/n] ")

            if response == 'n':
                sys.exit(1)

            _write_config(config_file)

        try:
            config.read(config_file)
        except configparser.MissingSectionHeaderError:
            print(f"{config_file} is an invalid config file.")
            sys.exit(1)

    config_dict = {}
    config_dict['duration'] = config.getint('Settings', 'duration')
    config_dict['spout_count'] = config.getint('Settings', 'spout_count')
    config_dict['iti'] = json.loads(config.get('Settings', 'iti'))
    config_dict['json_path'] = config.get('Settings', 'json_path')
    config_dict['reward_duration_ms'] = json.loads(
        config.get('Settings', 'reward_duration_ms')
    )

    return config_dict
