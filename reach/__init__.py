"""
The library exports four classes:

:class:`Session` objects are used to control raspberry pi hardware for a single
training session of the reaching task. They subsequently handle the data
collected from these sessions, and expose some properties that can provide
access to basic results such as reaction times. See `here <./training.html>`_
for information on how to run a new training session.

:class:`Mouse` objects handle and manipulate a :class:`list` of
:class:`Session` objects, and read/write their data to/from the mouse's
training JSON file. Additionally, they provide access to basic results across
sessions for a single mouse.

:class:`Cohort` objects handle and manipulate a :class:`list` of :class:`Mouse`
objects and are intended to be used for post-training analysis of behavioural
data in user scripts. See :repo:`scripts/plotting/cohort_reaction_times.py
<blob/master/scripts/plotting/cohort_reaction_times.py>` for an example.

:class:`UtilityPi` contains utilities that are used to perform testing of the
training box hardware. See :repo:`scripts/utilities/
<tree/master/scripts/utilities>` for scripts that perform individual tests.

"""

__version__ = '2019.10.01.0'

from reach.cohort import Cohort
from reach.mouse import Mouse
from reach.session import Session
from reach.raspberry import UtilityPi

__all__ = [
    'Cohort',
    'Mouse',
    'Session',
    'UtilityPi',
]
