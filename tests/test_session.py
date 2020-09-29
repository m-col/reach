# pylint: disable=redefined-outer-name
"""
Tests for reach.session
"""

import pytest

import reach.session
from reach import Session


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
    recent_trials.extend(session.data['trials'])
    assert len(recent_trials) == reach.session.SlidingTrialList.WINDOW
    assert recent_trials.get_hit_rate() == 0.7333333333333333


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
    assert results.get('correct') == 1
    assert results.get('incorrect') == 1
    assert results.get('missed') == 1
    assert results.get('resets_l') == 4
    assert results.get('spontaneous_reaches_l') == 4


def test_get_trials(session):
    trials = session.get_trials()
    assert all(isinstance(i, dict) for i in trials)


def test_get_d_prime(session):
    d_prime = session.get_d_prime()
    assert d_prime == 2.31348411534963


def test_get_results(session):
    results = session.get_results()
    assert isinstance(results, dict)
    assert results.get('duration') == 1800
    assert results.get('intertrial_interval') == [3000, 5000]
    assert results.get('start_time') == "16:30:37"
    assert results.get('end_time') == "17:00:37"
    assert results.get('correct') == 41
    assert results.get('incorrect') == 6
    assert results.get('missed') == 29
    assert results.get('resets_r') == 239
    assert results.get('spontaneous_reaches_r') == 56


def test_print_results(session):
    # This function is not super important so it's fine as long as it doesn't fail.
    reach.session.print_results(session)
