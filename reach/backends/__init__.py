"""
Backends
========

class:`Backends` represent and control the hardware used for the task, and can be
anything (hardware or software-controlling) as long as they subclass from
:class:`Backend`.

To create a new backend, copy this file and re-implement some or all of the methods as a
subclass.
"""


__all__ = ("Backend",)


class Backend:
    """
    This base class is the basis for all backends and is not intended for direct use by
    a training session. See `Backends <backends.html>`_ for information on how to use.

    Spout number can be 0 for the left spout or 1 for the right spout.
    """

    def __init__(self):
        self.on_iti_lift = None
        self.on_iti_grasp = None
        self.on_trial_lift = None
        self.on_trial_correct = None
        self.on_trial_incorrect = None

    def configure_callbacks(self, session):
        """
        Configure callback functions passed from the session. Callback functions should
        be executed during the intertrial-interval or trial at specific events, as per
        their name. The callbacks should be enabled in :class:`backend.start_iti` and
        :class:`backend.start_trial`, so these should have access to the session
        functions. The functions can be modified/wrapped to meet the specific needs of
        the backend. These are required for base functionality:

            - :class:`session.on_iti_lift`
            - :class:`session.on_iti_grasp`
            - :class:`session.on_trial_lift`
            - :class:`session.on_trial_correct`
            - :class:`session.on_trial_incorrect`

        """

    def wait_to_start(self):
        """
        Called once before the training session begins.
        """

    def position_spouts(self, position, spout_number=None):
        """
        Called to move one or both spouts to a specified position.

        Parameters
        ----------
        position : :class:`int`
            Millimetres from the mouse: integers from 1 to 7 inclusive.

        spout_number : :class:`int`, optional
            The spout to move. By default, both are moved.

        """

    def wait_for_rest(self):
        """
        Called to wait for the mouse to remain still during the inter-trial interval
        before counting down to the start of a trial. Must return True, or False due to
        a session cancellation.
        """
        return True

    def start_iti(self):
        """
        Assign :class:`session.on_iti_lift` and :class:`session.on_iti_grasp` callbacks
        to events.
        """

    def start_trial(self, spout_number):
        """
        Assign :class:`session.on_trial_lift`, :class:`session.on_trial_correct` and
        :class:`session.on_trial_incorrect` callbacks to events.

        This begins a trial: this can be used to the handle cue(s), record the time etc.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """

    def give_reward(self, spout_number):
        """
        Give a reward.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number to give reward from.

        """

    def miss_trial(self):
        """
        Called on a miss trial: when the trial ends and no spouts have been grasped.
        Note this is distinct from an incorrect trial, when the wrong spout was grasped.
        """

    def end_trial(self):
        """
        Called at the end of each trial.
        """

    def cleanup(self):
        """
        Called once at the end of the session.
        """
