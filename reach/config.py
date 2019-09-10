"""
Training Configuration files
============================

:class:`.Config` objects handle training session configuration through config
files.

"""


import configparser
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
    config.set('Settings', 'reward_duration_ms', 220)
    config.set('Settings', 'cue_duration_ms', 10000)
    config.set('Settings', 'iti', '4000, 6000')
    config.set('Settings', 'shaping', False)
    config.set('Settings', 'json_dir',
               '/home/pi/CuedBehaviourAnalysis/Data/TrainingJSON')

    return config


def _write_config(config_file, config=None):
    """
    Write configuration to file.

    Parameters
    ----------
    config_file : :class:`string`
        Path to file where config will be stored.

    config : :class:``, optional
        The configuration settings that will be stored. Default settings will
        be stored if this is not given.

    """

    if isfile(config_file):
        print(f"Config file {config_file} already exists.")
        confirm = input('Overwrite? (y/N) ')
        if confirm not in ['y', 'Y']:
            raise SystemError('Cancelled')

    if config is None:
        config = _default_config()
    else:
        config_dict['iti'] = ','.join([str(i) for i in config_dict['iti']])

    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print(f"A new config file has been generated as {config_file}.")


def read_config(config_file):
    """
    Read settings from config file and return as dict.

    Parameters
    ----------
    config_file : :class:`string` or :class:`None`
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
                raise SystemError
            else:
                _write_config(config_file)

        try:
            config.read(config_file)
        except configparser.MissingSectionHeaderError:
            raise SystemError(f"{config_file} is an invalid config file.")

    config_dict = {}
    config_dict['duration'] = config.getint('Settings', 'duration')
    config_dict['spout_count'] = config.getint('Settings', 'spout_count')
    config_dict['reward_duration_ms'] = config.getint('Settings', 'reward_duration_ms')
    config_dict['cue_duration_ms'] = config.getint('Settings', 'cue_duration_ms')
    config_dict['iti'] = config.get('Settings', 'iti')
    config_dict['iti'] = [int(i) for i in config_dict['iti'].split(',')]
    config_dict['shaping'] = config.getboolean('Settings', 'shaping')
    config_dict['json_dir'] = config.get('Settings', 'json_dir')

    #config_dict = dict(config.items('Settings'))
    #config_dict['iti'] = [int(i) for i in config_dict['iti'].split(',')]
    

    return config_dict