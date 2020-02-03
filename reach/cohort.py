"""
Cohorts
=======

:class:`Cohort`\s store multiple :class:`Mouse` instances for easier handling of mutiple
mice. Iterating over a cohort returns its :class:`Mouse` instances.
"""


from collections.abc import Sequence

from reach.mouse import Mouse
from reach.utilities import cache


class Cohort(Sequence):
    """
    Represents a cohort of multiple mice who have undergone behavioural training. These
    can be indexed to easily access a specific mouse.

    Parameters
    ---------------------
    mice : :class:`list` of :class:`Mouse` instances, optional
        A list containing a :class:`Mouse` intance for each mouse in the cohort.

    mouse_ids : :class:`list` of :class:`str`\s, optional
        A list of mouse IDs.

    """

    def __init__(self, mice=None, mouse_ids=None):
        self.mice = mice or []
        self.mouse_ids = mouse_ids or []

    @classmethod
    def init_from_files(cls, data_dir=None, mouse_ids=None):
        """
        Initialise the cohort of mice using training files stored within the same
        folder.

        Parameters
        ----------
        data_dir : :class:`str`
            Directory containing the training data files.

        mouse_ids : :class:`list` of :class:`str`\s
            IDs for the mice to be handled within the cohort.

        """
        mice = []

        for mouse in mouse_ids:
            mice.append(
                Mouse.init_from_file(
                    data_dir=data_dir,
                    mouse_id=mouse,
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

    @cache
    def outcomes(self):
        """
        Get trial outcomes for all mice across all sessions.
        """
        outcomes = []
        for mouse in self.mice:
            outcomes.append(mouse.outcomes)
        return outcomes

    @cache
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
            trials = trials.append(mouse_df.assign(mouse_id=self.mouse_ids[i]))

        return trials

    @cache
    def results(self):
        import pandas as pd  # pylint: disable=import-outside-toplevel
        results = pd.DataFrame()

        for i, mouse in enumerate(self.mice):
            session_results = []
            for j, session in enumerate(mouse.training_data):
                session_results.append(
                    dict(
                        day=j + 1,
                        trials=len(session.data['trials']),
                        trainer=session.data['trainer'],
                        weight=session.data['weight'],
                        training_box=session.data['training_box'],
                        duration=session.data['duration'],
                        iti=session.data['iti'],
                        resets=len(session.data['resets']),
                        resets_l=len([x for x in session.data['resets'] if x[1] == 0]),
                        resets_r=len([x for x in session.data['resets'] if x[1] == 1]),
                        spontaneous_reaches=len(session.data['spontaneous_reaches']),
                        spontaneous_reaches_l=len(
                            [x for x in session.data['spontaneous_reaches'] if x[1] == 0]
                        ),
                        spontaneous_reaches_r=len(
                            [x for x in session.data['spontaneous_reaches'] if x[1] == 1]
                        ),
                        start_time=session.data['start_time'],
                        end_time=session.data['end_time'],
                        missed=mouse.outcomes[j].count(0),
                        correct=mouse.outcomes[j].count(1),
                        incorrect=mouse.outcomes[j].count(2),
                        mouse_id=self.mouse_ids[i],
                    )
                )
            results = results.append(pd.DataFrame(session_results))

        results['hit_rate'] = results['correct'] / results['trials']
        return results
