"""
Training Configuration files
============================

:class:`.Config` objects handle training session configuration through config
files.

"""


import configparser
from os.path import isfile


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
    config.set('Settings', 'iti_min_ms', 4000)
    config.set('Settings', 'iti_max_ms', 6000)
    config.set('Settings', 'shaping', False)
    config.set('Settings', 'json_dir',
               '/home/pi/CuedBehaviourAnalysis/Data/TrainingJSON')

    return config


def _write_config(config_file, config=None):
    """
    Write configuration to file.
    """

    if isfile(config_file):
        print(f"Config file {config_file} already exists.")
        confirm = input('Overwrite? (y/N) ')
        if confirm not in ['y', 'Y']:
            raise SystemError('Cancelled')

    if config is None:
        config = _default_config()

    with open(config_file, 'w') as new_file:
        config.write(new_file)
    print(f"A new config file has been generated as {config_file}.")


def _read_config(config_file):
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
        if not isfile(config_file):
            raise SystemError(f"{config_file} config file does not exist.")

        try:
            config.read(config_file)
        except configparser.MissingSectionHeaderError:
            raise SystemError(f"{config_file} is an invalid config file.")

    config_dict = dict(config.items('Settings'))
    config_dict['iti'] = (config_dict['iti_min_ms'],
                          config_dict['iti_max_ms'])

    return config_dict
