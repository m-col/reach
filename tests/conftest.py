"""
Basic setup for testing.
"""

from pathlib import Path

import pytest


@pytest.fixture
def data_dir():
    yield Path(__file__).absolute().parent


@pytest.fixture
def mouse_id():
    yield 'mouse001'
