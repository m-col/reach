"""
Tests for reach.mouse
"""

from reach import Mouse, Session


def test_mouse(mouse):
    assert isinstance(mouse, Mouse)
    assert len(mouse) == 8
    assert all(isinstance(i, Session) for i in mouse)


def test_train(mouse):
    # TODO
    pass


def test_save_data_to_file(mouse):
    # TODO
    pass


def test_get_reaction_times(mouse):
    rts = mouse.get_reaction_times()
    assert len(rts) == 8  # 8 sessions
    assert all(isinstance(t, float) for s in rts for t in s)


def test_get_outcomes(mouse):
    outcomes = mouse.get_outcomes()
    assert len(outcomes) == 8  # 8 sessions
    assert all(isinstance(t, int) for s in outcomes for t in s)


def test_get_trials(mouse):
    # TODO after updating Cohort.get_trials and adding Mouse.get_trials
    pass


def test_get_results(mouse):
    results = mouse.get_results()
    assert len(results) == 8  # 8 sessions
    assert all(isinstance(i, dict) for i in results)
