"""
Sessions
========

:class:`.Session` objects interface with a raspberry pi to sequence training
sessions and record data.

"""


import json


class Session:
    """
    Controls a single training session and its behavioural data.

    Attributes
    ----------
    session_data : List of :class:`.Session` objects.
        This mouse's training data.

    Parameters
    ----------
    session_data : List of :class:`.Session` objects.
        Passed to pre-fill the session_data attribute with existing data.

    """

    def __init__(self, session_data=None):
        self._session_data = session_data

    @classmethod
    def init_all_from_file(cls, json_path):
        """
        Generate list of Session objects from data stored in Training JSON.

        Parameters
        ----------
        json_path : :class:`str`
            Training JSON to read data from.

        """
        with open(json_path, 'r') as json_file:
            file_data = json.load(json_file)

        training_data = [
            cls(session_data=session_data) for session_data in file_data
        ]

        return training_data
        

    def run(self, config):
        """
        Begin a training session.

        Parameters
        ----------
        config : :class:`dict`
            List of configuration parameters.

        """
