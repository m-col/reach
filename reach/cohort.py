"""
Cohorts
=======

:class:`.Cohort` objects store multiple :class:`.Mouse` objects for easier
handling of mutiple mice. It can be iterated over, yielding its :class:`.Mouse`
instances.

"""


from collections.abc import Sequence

from reach.mouse import Mouse


class Cohort(Sequence):
    """
    Represents a cohort of multiple mice who have undergone behavioural
    training.

    Attributes
    ----------
    mouse_ids : :class:`list` of :class:`str`s
        The list of mouse IDs, which is passed to initialise the instance.

    mice : :class:`list` of :class:`.Mouse` instances
        A list containing a :class:`.Mouse` intance for each mouse, storing all
        of their training data.

    """

    def __init__(self, mice=None, mouse_ids=None):
        """
        Initialise a cohort of mice for analysis.

        Parameters
        ----------
        mice : :class:`list` of :class:`Mouse` instances
            The mice to be included in the cohort, whose data we are going to
            handle.

        mouse_ids : :class:`list` of :class:`str`s
            List of mouse IDs corresponding to the mice to be handled.

        """
        self.mouse_ids = mouse_ids
        self.mice = mice

    @classmethod
    def init_from_files(cls, json_path=None, mouse_ids=None):
        """
        Initialise the cohort of mice using training JSON files stored within
        the same folder.
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
        Allow indexing directly, returning the nth :class:`.Mouse`
        """
        return self.mice[key]

    def __len__(self):
        """
        Allow querying of the size of the cohort.
        """
        return len(self.mice)
