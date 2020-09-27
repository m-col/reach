# pylint: disable=redefined-outer-name
"""
Tests for reach.mouse
"""

import os
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


def test_save_data_to_file(mouse, mouse_id):
    data_dir = tempfile.gettempdir()
    mouse.save_data_to_file(data_dir)
    new_mouse = Mouse.init_from_file(data_dir, mouse_id)
    new_data = [s.data for s in new_mouse.data]
    old_data = [s.data for s in mouse.data]
    assert new_data == old_data
    os.remove(os.path.join(data_dir,  mouse_id + '.json'))


def test_get_trials(mouse):
    i = 1
    for t in mouse.get_trials():
        assert isinstance(t, dict)
        day = t.get("day")
        assert day >= i
        i = day


def test_get_results(mouse):
    results = mouse.get_results()
    assert len(results) == 8  # 8 sessions
    assert all(isinstance(i, dict) for i in results)
