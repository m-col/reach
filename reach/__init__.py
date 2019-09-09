"""
Visually-guided reaching task for mice

This library exports three classes:

:class:`Session` objects are used to control raspberry pi hardware for a single
training session of the visually-guided reaching task for mice. They
subsequently handle the data collected from these sessions, and expose some
properties that can provide access to basic results such as reaction times. See
scripts/run_session.py for example usage during training.

:class:`Mouse` objects handle a list of :class:`Session` objects, and
read/write their data to/from training JSON file for the mouse. Additionally,
they provide access to basic results across sessions for a single mouse.

:class:`Cohort` objects handle a list of :class:`Mouse` objects and are
intended to be used for post-training analysis of behavioural data in user
scripts outside of the library. See scripts/plotting/cohort_reaction_times.py
for an example.

"""

__version__ = '2019.09.08.0'

from reach.cohort import Cohort
from reach.mouse import Mouse
from reach.session import Session

__all__ = [
    'Cohort',
    'Mouse',
    'Session',
]
