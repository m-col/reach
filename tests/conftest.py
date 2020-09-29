"""
Basic setup for testing.
"""

import time
from pathlib import Path

import pytest

from reach import Session
from reach.backends import Backend


@pytest.fixture(scope='session')
def data_dir():
    return Path(__file__).absolute().parent


@pytest.fixture
def mouse_id():
    return 'mouse001'


@pytest.fixture
def backend():
    return TestBackend()


class TestBackend(Backend):
    """
    This testing backend tests all possible trial outcomes, of which there are 4, as
    represented by reach.session.Outcomes. These are:

     - missed
     - correct
     - incorrect
     - cancelled

    We do 4 trials and end the session in the middle of the 4th. To imitate 10s of time
    during a trial, we hijack time.time and increment the fake_now variable by 10000,
    returning its new value each time. time.time is called once at the beginning, 4
    times per trial, and once during any of the on_* Session methods. At certain
    fake_now values we imitate events happening to the backend by executing session
    callbacks, to test these. (This is ugly, I know).

    """
    def message(self, msg):
        assert isinstance(msg, str)
        self.messaged = True
        print(msg)

    def configure_callbacks(self, session):
        assert isinstance(session, Session)
        self.session = session
        self.messaged = False

        # disable sleeping
        def noop(_):
            pass
        self.sleep = time.sleep
        time.sleep = noop

        # make time.time() always increment by 10000 (see docstring above)
        fake_now = 0
        def fake_time():
            nonlocal fake_now
            fake_now += 10000
            if fake_now == 80000:  # trigger a correct trial
                self.session.on_trial_lift(0)  # contains 1 time.time
                self.session.on_trial_correct()  # contains 1 time.time
                fake_now -= 20000
            elif fake_now == 140000:  # trigger an incorrect trial
                self.session.on_trial_lift(1)  # contains 1 time.time
                self.session.on_trial_incorrect()  # contains 1 time.time
                fake_now -= 20000
            elif fake_now == 200000:  # end the session prematurely
                self.session._end_session()  # contains 1 time.time
                fake_now -= 10000
            return fake_now
        self.time = time.time
        time.time = fake_time

    def wait_for_rest(self):
        self.session.on_iti_lift(0)  # contains 1 time.time
        self.session.on_iti_grasp(0)  # contains 1 time.time
        return True

    def position_spouts(self, position, spout_number=None):
        assert isinstance(position, int)
        assert 0 <= position <= 7
        assert spout_number is None

    def start_trial(self, spout_number):
        assert spout_number == 0 or spout_number == 1

    def give_reward(self, spout_number):
        assert spout_number == 0 or spout_number == 1

    def cleanup(self):
        time.sleep = self.sleep
        time.time = self.time
        assert self.messaged
