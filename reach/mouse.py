"""
Mice
====

:class:`.Mouse` objects store and handle training sessions and collected data
for a single experimental mouse.

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
    training_data : List of :class:`.Session` objects.
        This mouse's training data.

    """

    def __init__(self, mouse_id=None, training_data=None):
        self._training__data = training_data


    @classmethod
    def init_from_file(cls, mouse_id=None, json_path=None):
        """
        Initialise Mouse object using pre-existing training data stored within
        a training JSON.
        """

        if os.path.isfile(json_path):
            training_data = Session.init_all_from_file(json_path)
            return cls(mouse_id=mouse_id, training_data=training_data)

        else:
            return cls(mouse_id=mouse_id)


    def train(self, config_file):
        """
        Start reaching training session.
        """
        config = _read_config(config_file)
        session = Session()
        session.run(config)


    def add_session_data(self, new_session_data):
        """
        Append data from new session to mouse session data.
        """
        new_session = Session(new_session_data)
        self.training_data.append(new_session)
