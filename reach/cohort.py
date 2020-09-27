"""
Cohorts
=======

:class:`Cohort`\s store multiple :class:`Mouse` instances for easier handling of mutiple
mice. Iterating over a cohort returns its :class:`Mouse` instances.
"""

from collections.abc import Sequence

from reach.mouse import Mouse


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
    def init_from_files(cls, data_dir, mouse_ids):
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
        if isinstance(mouse_ids, str):
            mouse_ids = [mouse_ids]

        for mouse in mouse_ids:
            mice.append(Mouse.init_from_file(data_dir=data_dir, mouse_id=mouse,))

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

    def get_trials(self):
        """
        Get trial data for all mice across all sessions.

        This can easily be turned into a useful pandas DataFrame:
        >>> trials = pd.DataFrame(cohort.get_trials())
        """
        return (i for mouse in self.mice for i in mouse.get_trials())

    def get_results(self):
        """
        Get the high-level results for all training sessions for all mice.

        This can easily be turned into a useful pandas DataFrame:
        >>> results = pd.DataFrame(cohort.get_results())
        """
        return (i for mouse in self.mice for i in mouse.get_results())
