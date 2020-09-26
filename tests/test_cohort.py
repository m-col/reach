# pylint: disable=redefined-outer-name
"""
Tests for reach.cohort
"""

import pytest

from reach import Cohort, Mouse, Session


@pytest.fixture
def cohort(data_dir, mouse_id):
    c = Cohort.init_from_files(data_dir, [mouse_id])
    yield c


def test_cohort(cohort):
    assert isinstance(cohort, Cohort)
    assert len(cohort) == 1
    assert isinstance(cohort[0], Mouse)
    assert cohort.mouse_ids[0] == cohort[0].mouse_id
    assert isinstance(cohort[0][0], Session)


def test_get_reaction_times(cohort):
    rts = list(cohort.get_reaction_times())
    assert len(rts) == 1  # 1 mouse
    assert len(rts[0]) == 8  # 8 sessions
    assert all(isinstance(t, float) for s in rts[0] for t in s)


def test_get_outcomes(cohort):
    outcomes = cohort.get_outcomes()
    assert len(outcomes) == 1  # 1 mouse
    assert len(outcomes[0]) == 8  # 8 sessions
    assert all(isinstance(t, int) for s in outcomes[0] for t in s)


def test_get_trials(cohort):
    # TODO after updating Cohort.get_trials
    pass


def test_get_results(cohort):
    results = list(cohort.get_results())
    assert len(results) == 8  # 8 sessions
    assert all(isinstance(i, dict) for i in results)
    # Cohort.get_results gives a flattened list, and we only have 1 mouse, so these
    # should be the same
    assert results == cohort[0].get_results()
