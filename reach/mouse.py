"""
Mice
====

:class:`.Mouse` objects store and handle training sessions and collected data
for a single experimental mouse. They were used to start training sessions
using the :class:`Mouse.train()` method.

"""


import json
import textwrap
from os.path import isdir, isfile, join

from reach.config import read_config
from reach.session import Session
from reach.utilities import lazy_property, enforce_suffix


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

    def __init__(self, mouse_id=None, training_data=None):

        if training_data is None:
            training_data = []

        self.mouse_id = mouse_id
        self._training_data = training_data

    @classmethod
    def init_from_file(cls, json_path=None, mouse_id=None):
        """
        Initialise Mouse object using pre-existing training data stored within
        a training JSON.
        """
        if mouse_id is None:
            raise SystemError(
                "mouse_id must contain a string to use Mouse.init_from_file"
            )

        if isfile(json_path):
            training_data = Session.init_all_from_file(
                json_path=json_path
            )
            return cls(mouse_id=mouse_id, training_data=training_data)

        if isdir(json_path):
            full_path = join(json_path, mouse_id)
            full_path = enforce_suffix(full_path, '.json')

            if isfile(full_path):
                training_data = Session.init_all_from_file(
                    json_path=full_path
                )
                return cls(mouse_id=mouse_id, training_data=training_data)

            print(f"File {full_path} not found.")
        else:
            print(f"File {json_path} not found.")

        print("Initialising empty Mouse object.")
        return cls(mouse_id=mouse_id)

    def train(self, config_file=None, metadata=None):
        """
        Start reaching training session and add new data to training data.

        Parameters
        ----------
        config_file : :class:`str`, optional
            Path to the configuration file containing training settings.

        metadata : :class:`dict`, optional
            Extra metadata that should be saved into the new session's data.

        """

        if self.mouse_id is not None:
            print(f'Training mouse: {self.mouse_id}')

        config = read_config(config_file)
        new_session = Session(metadata=metadata)
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

        if isfile(enforce_suffix(json_path, '.json')):
            full_path = enforce_suffix(json_path, '.json')

        elif isdir(json_path):
            full_path = join(
                json_path,
                enforce_suffix(self.mouse_id, '.json')
            )

        else:
            full_path = 'temp_data.json'
            print(textwrap.dedent(f"""
            Could not determine correct JSON path from:")
                json_path: {json_path}
                mouse_id:  {self.mouse_id}
            Saved data into {full_path}"""))

        data = [i.data for i in self._training_data]

        with open(full_path, 'w') as json_file:
            json.dump(data, json_file)

        print(f"Data was saved in {full_path}")

    def get_session_reaction_times(self, session_number):
        """
        Get reaction times for a training session.

        Parameters
        ----------
        session_number : :class:`int`
            The session number for the session we are want RTs for.

        Returns
        -------
        :class:`list` of :class:`ints`s
            Chronological list of reaction times in milliseconds.

        """
        session = self._training_data[session_number]
        return session.reaction_times

    @lazy_property
    def reaction_times(self):
        """
        Get reaction times for all training sessions.

        Returns
        -------
        :class:`list` of :class:`list`s of :class:`int`s
            Each list contains chronological list of reaction times in
            milliseconds for the nth training session.

        """
        reaction_times = []

        for session in self._training_data:
            reaction_times.append(session.reaction_times)

        return reaction_times
