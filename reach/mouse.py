"""
Mice
====

Mouse objects store and handle training sessions and collected data for a single
experimental mouse. They are used to start training sessions using the
:class:`Mouse.train()` method.
"""


import json
import os
import tempfile

from reach.session import Session
from reach.utilities import cache


class Mouse:
    """
    This class represents a single experimental mouse. Mouse instances can be
    instantiated either by providing training data manually, or with
    :class:`Mouse.init_from_file` to use training data stored in a file.

    Training data is stored as a list of :class:`Session` instances.

    Attributes
    ----------
    mouse_id : :class:`str`, optional
        The mouse's ID.

    training_data : :class:`list` of :class:`Session` instances.
        The mouse's training data.

    """

    def __init__(self, mouse_id=None, training_data=None):
        if training_data is None:
            training_data = []

        self.mouse_id = mouse_id
        self.training_data = training_data

    def __getitem__(self, index):
        """
        Allow indexing directly, returning the nth :class:`Session`
        """
        return self.training_data[index]

    def __len__(self):
        """
        Allow querying of the number of training days completed.
        """
        return len(self.training_data)

    @classmethod
    def init_from_file(cls, data_dir, mouse_id):
        """
        Initialise Mouse object using pre-existing training data stored within
        a training JSON.

        Parameters
        ----------

        data_dir : :class:`str`
            Directory containing training data.

        mouse_id : :class:`str`
            Mouse ID to pass to :class:`Mouse` instance. Will be used to find
            JSON if json_path is a folder.

        """
        if not os.path.isdir(data_dir):
            raise SystemError(f"Could not find directory {data_dir}")

        data_file = os.path.join(data_dir, f"{mouse_id}.json")

        if os.path.isfile(data_file):
            training_data = Session.init_all_from_file(data_file)
            mouse = cls(mouse_id=mouse_id, training_data=training_data)

        else:
            print("Initialising empty Mouse object.")
            mouse = cls(mouse_id=mouse_id)

        return mouse

    def train(
        self,
        backend,
        additional_data=None,
        duration=None,
        intertrial_interval=None,
        hook=None,
        timeout=None,
    ):
        """
        Create a new Session and run it, appending its newly-collected data to the
        Mouse's training data.

        Parameters
        ----------
        backend : :class:`class`
            An instance of a Backend subclass.

        additional_data : :class:`dict`, optional
            Extra data that should be saved into the new session's data.

        duration : :class:`int`, optional
            The duration in seconds for the training session to run.

        intertrial_interval : :class:`tuple` of 2 :class:`int`\s, optional
            Min. and max. duration in milliseconds for the inter-trial intervals e.g.
            (4000, 6000)

        hook : :class:`callable`, optional
            An object that will be called at the end of every trial.

        timeout : :class:`callable`, optional
            Duration in milliseconds of a timeout to wait after an incorrect trial.

        """

        if self.mouse_id:
            print(f"Training mouse: {self.mouse_id}")

        if self.training_data:
            previous_data = self.training_data[-1].data
        else:
            previous_data = None

        new_session = Session()

        if additional_data is not None:
            new_session.add_data(additional_data)

        self.training_data.append(new_session)
        new_session.run(
            backend,
            previous_data=previous_data,
            duration=duration,
            intertrial_interval=intertrial_interval,
            hook=hook,
            timeout=timeout,
        )

    def save_data_to_file(self, data_dir):
        """
        Save all training data to training JSON file.

        Parameters
        ----------
        data_dir : :class:`str`
            Directory into which to save training data.

        """
        data = [i.data for i in self.training_data]

        try:
            path = os.path.join(data_dir, f"{self.mouse_id}.json")
            with open(path, "w") as fd:
                json.dump(data, fd)
        except FileNotFoundError:
            path = os.path.join(tempfile.tempdir(), f"{self.mouse_id}.json")
            with open(path, "w") as fd:
                json.dump(data, fd)

        print(f"Data was saved in {path}")

    def get_session_reaction_times(self, session_number):
        """
        Get reaction times for a training session.

        Parameters
        ----------
        session_number : :class:`int`
            The session number for the session we are want reaction times for.

        Returns
        -------
        :class:`list` of :class:`ints`\s
            Chronological list of reaction times in milliseconds.

        """
        session = self.training_data[session_number]
        return session.reaction_times

    @cache
    def reaction_times(self):
        """
        Get reaction times for all training sessions.

        Returns
        -------
        :class:`list` of :class:`list`\s of :class:`float`\s
            List containing one list of reaction times per session in
            milliseconds.

        """
        reaction_times = []

        for session in self.training_data:
            reaction_times.append(session.reaction_times)

        return reaction_times

    @cache
    def outcomes(self):
        """
        Get trial outcomes per session.

        Returns
        -------
        :class:`list` of :class:`lists`\s of :class:`int`\s
            Each inner list is one session, and contains for each trial an :class:`int`
            representing one possible outcome: 0, miss trial; 1, correct reach; and 2,
            incorrect reach.

        """
        return [session.outcomes for session in self.training_data]

    @cache
    def results(self):
        """
        Return training data for all sessions in a pandas DataFrame.

        Returns
        -------
        :class:`list` of :class:`dict`\s
            Each dict is :class:`Session.results`, with the day number and mouse ID
            added.

        """
        results = []
        for day, session in enumerate(self.training_data):
            session.results["day"] = day + 1
            session.results["mouse_id"] = self.mouse_id
            results.append(session.results)
        return results
