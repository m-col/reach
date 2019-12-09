"""
Cohorts
=======

:class:`.Cohort` objects store multiple :class:`.Mouse` objects for easier
handling of mutiple mice. It can be iterated over, yielding its :class:`.Mouse`
instances.

"""


from collections.abc import Sequence

from reach.mouse import Mouse
from reach.utilities import lazy_property


class Cohort(Sequence):
    """
    Represents a cohort of multiple mice who have undergone behavioural
    training. Cohort can be indexed to easily access a specific mouse.

    Attributes
    ----------
    mouse_ids : :class:`list` of :class:`str`\s
        A list of mouse IDs.

    mice : :class:`list` of :class:`.Mouse` instances
        A list containing a :class:`.Mouse` intance for each mouse in the
        cohort.

    """

    def __init__(self, mice=None, mouse_ids=None):
        """
        Initialise a cohort of mice for analysis.

        Parameters
        ----------
        mice : :class:`list` of :class:`Mouse` instances
            The mice to be included in the cohort, whose data we are going to
            handle.

        mouse_ids : :class:`list` of :class:`str`\s
            List of mouse IDs corresponding to the mice to be handled.

        """
        self.mouse_ids = mouse_ids
        self.mice = mice

    @classmethod
    def init_from_files(cls, json_path=None, mouse_ids=None):
        """
        Initialise the cohort of mice using training JSON files stored within
        the same folder.

        Parameters
        ----------
        json_path : :class:`str`
            Path to the folder containing the training JSONs.

        mouse_ids : :class:`list` of :class:`str`\s
            IDs for the mice to be handled within the cohort.

        """
        mice = []

        for mouse in mouse_ids:
            mice.append(
                Mouse.init_from_file(
                    mouse_id=mouse,
                    json_path=json_path
                )
            )

        return cls(mice, mouse_ids)

    def __getitem__(self, key):
        """
        Allow indexing directly, returning the nth :class:`Mouse`
        """
        return self.mice[key]

    def __len__(self):
        """
        Allow querying of the size of the cohort.
        """
        return len(self.mice)

    def __repr__(self):
        return f"Cohort containing mice: {', '.join(self.mouse_ids)}"

    @lazy_property
    def outcomes(self):
        """
        Get trial outcomes for all mice across all sessions.
        """
        outcomes = []
        for mouse in self.mice:
            outcomes.append(mouse.outcomes)
        return outcomes

    @lazy_property
    def trials(self):
        """
        Get trial data for all mice and sessions as a pandas DataFrame.
        """
        import pandas as pd  # pylint: disable=import-outside-toplevel
        trials = pd.DataFrame()

        for i, mouse in enumerate(self.mice):
            mouse_df = pd.DataFrame()
            for j, session in enumerate(mouse.training_data):
                df = pd.DataFrame(session.data['trials'])
                mouse_df = mouse_df.append(df.assign(day=j + 1), sort=False)
            trials = trials.append(mouse_df.assign(mouse=self.mouse_ids[i]))

        return trials

    @lazy_property
    def results(self):
        import pandas as pd  # pylint: disable=import-outside-toplevel
        results = pd.DataFrame()

        for i, mouse in enumerate(self.mice):  # TODO
            mouse_df = pd.DataFrame()
            for j, session in enumerate(mouse.training_data):
                ses_results = {}
                ses_results['missed'] = mouse.outcomes[j].count(0)
                ses_results['correct'] = mouse.outcomes[j].count(1)
                ses_results['incorrect'] = mouse.outcomes[j].count(2)
            mouse_df.append(pd.DataFrame(ses_results))

        return results
