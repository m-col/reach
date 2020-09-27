# pylint: disable=redefined-outer-name
"""
Tests for reach.mouse
"""

import tempfile

import pytest

from reach import Mouse, Session


@pytest.fixture
def mouse(data_dir, mouse_id):
    m = Mouse.init_from_file(data_dir, mouse_id)
    yield m


def test_mouse(mouse):
    assert isinstance(mouse, Mouse)
    assert len(mouse) == 8
    assert all(isinstance(i, Session) for i in mouse)


def test_train(mouse):
    # TODO
    pass


def test_save_data_to_file(mouse):
    data_dir = tempfile.gettempdir()
    mouse.save_data_to_file(data_dir)
    new_mouse = Mouse.init_from_file(data_dir, mouse.mouse_id)
    new_data = [s.data for s in new_mouse.data]
    old_data = [s.data for s in mouse.data]
    assert new_data == old_data


def test_get_trials(mouse):
    # TODO after updating Cohort.get_trials and adding Mouse.get_trials
    pass


def test_get_results(mouse):
    results = mouse.get_results()
    assert len(results) == 8  # 8 sessions
    assert all(isinstance(i, dict) for i in results)
