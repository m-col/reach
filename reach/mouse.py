"""
Mice
====

:class:`.Mouse` objects store and handle training sessions and collected data
for a single experimental mouse.

The Mouse class is used during training using the :class:`Mouse.train()`
method.

It is also used to collect training data from the mouse's behavioural training.

"""


import json
import os

from .config import _read_config
from .session import Session


class Mouse:
    """
    Represents a single experimental mouse.

    Attributes
    ----------
    mouse_id : :class:`str`
        The mouse's ID. Can be specified as a kwarg.

    _training_data : :class:`list` of :class:`.Session` instances.
        This mouse's training data. Can be specified as a kwarg.

    """

    def __init__(self, mouse_id=None, training_data=[]):
        self.mouse_id = mouse_id
        self._training_data = training_data

    @classmethod
    def init_from_file(cls, json_path, mouse_id=None):
        """
        Initialise Mouse object using pre-existing training data stored within
        a training JSON.
        """

        if os.path.isfile(json_path):
            training_data = Session._init_all_from_file(json_path)
            return cls(mouse_id=mouse_id, training_data=training_data)

        else:
            return cls(mouse_id=mouse_id)

    def train(self, config_file=None):
        """
        Start reaching training session and add new data to training data.

        Parameters
        ----------
        config_file : :class:`str`
            Path to the configuration file containing training settings.

        """

        if self.mouse_id is not None:
            print(f'Training mouse: {self.mouse_id}')

        config = _read_config(config_file)
        new_session = Session()
        new_session.run(config)
        self._training_data.append(new_session)

    def save_data_to_file(self, json_path):
        """
        Save all training data to training JSON file.

        Parameters
        ----------
        json_path : :class:`str`
            Training JSON to write data to.

        """
        with open(json_path, 'w') as json_file:
            json.dump(self._training_data, json_file)
        print(f"Data was saved in {json_path}")

    def get_session_reaction_times(self, session_number):
        """
        Get reaction times for a training session.

        Parameters
        ----------
        session_number : :class:`int`
            The session number for the session we are want RTs for.

        Returns
        -------
        :class:`List` of :class:`Ints`s
            Chronological list of reaction times in milliseconds.

        """
        return self._training_data[session_number].reaction_times
