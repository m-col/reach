from pathlib import Path

import pytest

from reach import Cohort, Mouse

mouse_ids = ['mouse001']
data_dir = Path(__file__).absolute().parent


@pytest.fixture
def cohort():
    c = Cohort.init_from_files(data_dir, mouse_ids)
    yield c


@pytest.fixture
def mouse():
    m = Mouse.init_from_file(data_dir, mouse_ids[0])
    yield m
