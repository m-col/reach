# pylint: disable=redefined-outer-name
"""
Tests for reach.session
"""

import pytest

from reach.session import (
    Outcomes, Session, SlidingTrialList, Targets, print_results
)


@pytest.fixture
def session(data_dir, mouse_id):
    data_file = data_dir / f"{mouse_id}.json"
    sessions = Session.init_all_from_file(data_file)
    s = sessions[-1]
    yield s


def test_session(session):
    assert isinstance(session, Session)


def test_recent_trials(session):
    recent_trials = session._recent_trials  # pylint: disable=protected-access

    all_trials = [[], []]
    for trial in session.data['trials']:
        recent_trials[trial['spout']].append(trial)
        all_trials[trial['spout']].append(trial['outcome'])

    assert len(recent_trials[Targets.LEFT]) == SlidingTrialList.WINDOW
    assert len(recent_trials[Targets.RIGHT]) == SlidingTrialList.WINDOW

    for side in [Targets.LEFT, Targets.RIGHT]:
        win = all_trials[side][-SlidingTrialList.WINDOW:]
        hit_rate = win.count(Outcomes.CORRECT) / SlidingTrialList.WINDOW
        assert recent_trials[side].get_hit_rate() == hit_rate


def test_run(session, backend):
    hook_flag = 0
    def hook():
        nonlocal hook_flag
        hook_flag += 1

    session.run(
        backend,
        duration=10000000,
        intertrial_interval=(0, 0),
        timeout=0,
        hook=hook,
    )
    assert hook_flag == 4
    results = session.get_results()
    assert results['correct_l'] == 1
    assert results['correct_r'] == 0
    assert results['incorrect_l'] == 1
    assert results['incorrect_r'] == 0
    assert results['missed_l'] == 1
    assert results['missed_r'] == 0
    assert results['resets_l'] == 4
    assert results['spontaneous_reaches_l'] == 4


def test_get_trials(session):
    trials = session.get_trials()
    assert all(isinstance(i, dict) for i in trials)


def test_get_d_prime(session):
    d_prime = session.get_d_prime()
    assert d_prime == 2.31348411534963


def test_get_results(session):
    results = session.get_results()
    assert isinstance(results, dict)
    assert results['duration'] == 1800
    assert results['intertrial_interval'] == [3000, 5000]
    assert results['start_time'] == "16:30:37"
    assert results['end_time'] == "17:00:37"
    assert results['correct_l'] == 20
    assert results['correct_r'] == 21
    assert results['incorrect_l'] == 5
    assert results['incorrect_r'] == 1
    assert results['missed_l'] == 17
    assert results['missed_r'] == 12
    assert results['resets_r'] == 239
    assert results['spontaneous_reaches_r'] == 56


def test_get_spontaneous_reaches(session):
    sponts = session.get_spontaneous_reaches()
    locations = (Targets.LEFT, Targets.RIGHT)
    t = 0
    for s in sponts:
        assert s.get("timing") > t
        assert s.get("location") in locations
        t = s.get("timing")


def test_print_results(session):
    # This function is not super important so it's fine as long as it doesn't fail.
    print_results(session)
