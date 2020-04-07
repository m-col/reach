"""
The library exports  classes:


:class:`Session`\s control the sequence of events during a training session and track
training data throughout the session. They can then be used after a session has
completed for analysis of this training data. :class:`Session`\s must be provided with a
:class:`Backend` or a subclass thereof to control during training. See `Behavioural
Training <./training.html>`_ for how to do this.

:class:`Mouse` instances handle and manipulate a :class:`list` of :class:`Session`\s,
and read/write their data to and from the mouse's training JSON file. They provide
access to basic results across sessions for a single mouse.

:class:`Cohort`\s handle and manipulate a :class:`list` of :class:`Mouse` instances and
are intended to be used for post-training analysis of behavioural data in user scripts.
See :repo:`scripts/plotting/cohort_reaction_times.py
<blob/master/scripts/plotting/cohort_reaction_times.py>` for an example.

"""

__version__ = "2020-04-07.2"

from reach.cohort import Cohort
from reach.mouse import Mouse
from reach.session import Session

__all__ = [
    "Cohort",
    "Mouse",
    "Session",
]
