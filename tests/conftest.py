from pathlib import Path

import pytest

from reach import Cohort

mouse_ids = ['mouse001']
data_dir = Path(__file__).absolute().parent


@pytest.fixture
def cohort():
    c = Cohort.init_from_files(data_dir, mouse_ids)
    yield c
