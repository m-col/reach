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
        **kwargs,
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

        **kwargs : Additional keyword arguments are forwarded to Session.run()

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
            **kwargs,
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

    def get_trials(self, collapse_days: bool = True):
        """
        Get trial data for all sessions.

        This can easily be turned into a useful pandas DataFrame:
        >>> trials = pd.DataFrame(mouse.get_trials())

        collapse_days, if True, will merge the results of consecutive days if they share
        a date.
        """
        trials = []
        date = None
        day_decrement = 0

        for day, session in enumerate(self.data, start=1):
            ses_trials = session.get_trials()
            if ses_trials:
                if collapse_days:
                    if date == session.data["date"]:
                        day_decrement += 1
                    else:
                        date = session.data["date"]

                good_ses_trials = []
                for t in ses_trials:
                    if "outcome" in t:
                        t['day'] = day - day_decrement
                        t['mouse_id'] = self.mouse_id
                        for s, pos in enumerate(t['spout_position']):
                            t[f'spout_position_{s}'] = pos
                        good_ses_trials.append(t)

                trials.extend(good_ses_trials)

        return trials

    def get_results(self, collapse_days: bool = True):
        """
        Get the high-level results for all sessions.

        This can easily be turned into a useful pandas DataFrame:
        >>> results = pandas.DataFrame(mouse.get_results())

        collapse_days, if True, will merge the results of consecutive days if they share
        a date. WARNING: if this occurs, d' values for collapsed days would be invalid,
        and so are replaced with None for those days. These need to be re-calculated
        with the trials returned from get_trials().
        """
        results = []
        date = None
        if collapse_days:
            day_decrement = 0

        for day, session in enumerate(self.data, start=1):
            session_results = session.get_results()
            if "notes" not in session_results:
                session_results["notes"] = None

            if session_results:
                session_results["mouse_id"] = self.mouse_id

                if collapse_days:
                    if date == session_results["date"]:
                        results[-1]["trials"] += session_results["trials"]
                        results[-1]["duration"] += session_results["duration"]
                        results[-1]["resets"] += session_results["resets"]
                        results[-1]["missed_l"] += session_results["missed_l"]
                        results[-1]["missed_r"] += session_results["missed_r"]
                        results[-1]["correct_l"] += session_results["correct_l"]
                        results[-1]["correct_r"] += session_results["correct_r"]
                        results[-1]["incorrect_l"] += session_results["incorrect_l"]
                        results[-1]["incorrect_r"] += session_results["incorrect_r"]
                        results[-1]["resets_l"] += session_results["resets_l"]
                        results[-1]["resets_r"] += session_results["resets_r"]
                        results[-1]["spontaneous_reaches_l"] += session_results["spontaneous_reaches_l"]
                        results[-1]["spontaneous_reaches_r"] += session_results["spontaneous_reaches_r"]
                        results[-1]["spontaneous_reaches"] += session_results["spontaneous_reaches"]
                        results[-1]["end_time"] = session_results["end_time"]
                        results[-1]["notes"] = "{} ... {}".format(
                            results[-1]["notes"], session_results["notes"]
                        )
                        # We cannot reconstruct d prime with just this information, as
                        # we not know which trials are correction trials.
                        results[-1]["d_prime"] = None
                        day_decrement += 1
                    else:
                        session_results["day"] = day - day_decrement
                        date = session_results["date"]
                        results.append(session_results)

                else:
                    session_results["day"] = day
                    results.append(session_results)

        return results

    def get_spontaneous_reaches(self):
        """
        Get the data on spontaneous reach timings and locations for all sessions.

        This can easily be turned into a useful pandas DataFrame:
        >>> spontaneous_reaches = pd.DataFrame(mouse.get_spontaneous_reaches())
        """
        sponts = []
        for day, session in enumerate(self.data):
            session_sponts = session.get_spontaneous_reaches()
            for i in session_sponts:
                i['day'] = day + 1
                i['mouse_id'] = self.mouse_id
            sponts.extend(session_sponts)
        return sponts
