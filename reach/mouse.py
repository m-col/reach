"""
Mice
====

Mouse objects store and handle training sessions and collected data for a single
experimental mouse. They are used to start training sessions using the
:class:`Mouse.train()` method.
"""

import json
import tempfile
from pathlib import Path

from reach.session import Session


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

    data : :class:`list` of :class:`Session` instances.
        The mouse's training data.

    """
    def __init__(self, mouse_id=None, data=None):
        if data is None:
            data = []

        self.mouse_id = mouse_id
        self.data = data

    def __getitem__(self, index):
        """
        Allow indexing directly, returning the nth :class:`Session`
        """
        return self.data[index]

    def __len__(self):
        """
        Allow querying of the number of training days completed.
        """
        return len(self.data)

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
        data_dir = Path(data_dir)
        if not data_dir.exists():
            raise SystemError(f"Could not find directory {data_dir}")

        data_file = data_dir / f"{mouse_id}.json"

        if data_file.exists():
            data = Session.init_all_from_file(data_file)
            mouse = cls(mouse_id=mouse_id, data=data)

        else:
            print("Training a new mouse.")
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

        if self.data:
            previous_data = self.data[-1].data
        else:
            previous_data = None

        new_session = Session()

        if additional_data is not None:
            new_session.add_data(additional_data)

        self.data.append(new_session)
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
        data = [i.data for i in self.data]
        data_dir = Path(data_dir)

        def write(path):
            with path.open(mode='w') as fd:
                json.dump(data, fd)
            print(f"Data was saved in {path}")

        try:
            write(data_dir / f"{self.mouse_id}.json")
        except FileNotFoundError:
            write(Path(tempfile.gettempdir()) / f"{self.mouse_id}.json")
        except Exception as e:  # pylint: disable=broad-except
            write(Path(tempfile.gettempdir()) / f"{self.mouse_id}.json")
            print(f"Exception raised while saving: {type(e)}")
            print("Please report this.")

    def get_reaction_times(self):
        """
        Get reaction times for all training sessions.

        Returns
        -------
        :class:`list` of :class:`list`\s of :class:`float`\s
            List containing one list of reaction times per session in seconds.

        """
        reaction_times = []

        for session in self.data:
            reaction_times.append(session.get_reaction_times())

        return reaction_times

    def get_outcomes(self):
        """
        Get trial outcomes per session.

        Returns
        -------
        :class:`list` of :class:`lists`\s of :class:`int`\s
            Each inner list is one session, and contains for each trial an :class:`int`
            representing one possible outcome: 0, miss trial; 1, correct reach; and 2,
            incorrect reach.

        """
        return [session.get_outcomes() for session in self.data]

    def get_results(self):
        """
        Return training data for all sessions.

        Returns
        -------
        :class:`list` of :class:`dict`\s
            Each dict is the output from :class:`Session.get_results()`, with the day
            number and mouse ID added.

        """
        results = []
        for day, session in enumerate(self.data):
            session_results = session.get_results()
            session_results["day"] = day + 1
            session_results["mouse_id"] = self.mouse_id
            results.append(session_results)
        return results
