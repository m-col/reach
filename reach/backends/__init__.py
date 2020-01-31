"""
Backends
========

class:`Backends` typically represent and control the Raspberry Pi hardware used for the
task, though can be anything (hardware or software-controlling) that implements all
methods of the Backend class. All backends must subclass from :class:`Backend`.

To create a new backend, copy this file and re-implement some or all of the methods as a
subclass.

"""


__all__ = ('Backend',)


class Backend:
    """
    This base class is the basis for all backends.

    This class does nothing, so can be used as a fallback if other backends cannot be
    used e.g. if their dependencies are unavailable at runtime, however this might not
    be very useful.

    Backends can have additional methods added, which can be used to customise its
    behaviour before starting a training session.

    Callback functions
    ------------------
    Five Session methods should be executed at specific events:

        session.on_iti_lift
        session.on_iti_grasp
        session.on_trial_lift
        session.on_trial_correct
        session.on_trial_incorrect

    Additional session methods can be assigned to backend hardware such as buttons to
    add extra functionality to the session. Such as:

        session.reverse_shaping
        session.extend_trial

    """
    def __init__(self):
        self.on_iti_lift = None
        self.on_iti_grasp = None
        self.on_trial_lift = None
        self.on_trial_correct = None
        self.on_trial_incorrect = None

    def configure_callbacks(self, session):
        """
        Configure callback functions passed from Session. These may need to be wrapped
        to account for how they are executed by the backend.
        """
        pass

    def wait_to_start(self):
        """
        Called immediately before the training session begins.
        """
        pass

    def disable_spouts(self):
        """
        This can be used to disable power to the hardware controlling spout position.
        """
        pass

    def position_spouts(self, position, spout_number=None):
        """
        This can be used to move one or both spouts to a specified positon. Position is
        an int from 1 to 7 that represents millimetres from the mouse.
        """
        pass

    def wait_for_rest(self):
        """
        This method should be used to wait for the mouse to remain still during the
        inter-trial interval before counting down to the start of a trial.
        """
        pass

    def start_iti(self):
        """
        Handle callbacks during the inter-trial interval.
        """
        pass

    def start_trial(self, spout_number):
        """
        Illuminate a cue, record the time, and add callback functions to be executed
        upon grasp of target spouts during trial.

        This begins a trial: this can be used to handle cue(s), recording of any useful
        information.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number corresponding to this trial's reach target.

        """
        pass

    def dispense_water(self, spout_number):
        """
        Dispense water from a specified spout.

        Parameters
        ----------
        spout_number : :class:`int`
            The spout number to dispense water from i.e. 0 is left, 1 is right.

        """
        pass

    def miss_trial(self):
        """
        This is called on a miss trial: when the trial ends and no spouts have been
        grasped. Note this is distinct from an incorrect trial, when the wrong spout was
        grasped.
        """
        pass

    def end_trial(self):
        """
        This is called at the end of a trial.
        """
        pass

    def cleanup(self):
        """
        This is executed at the end of the session.
        """
        pass
