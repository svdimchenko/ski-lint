import pathlib

import pytest

TEST_PATH = pathlib.Path(__file__).parent.resolve()
BASE_PATH = TEST_PATH.parent


@pytest.fixture
def test_files_good():
    path = TEST_PATH / "files" / "good"
    return [p for p in path.glob("*.txt")]


@pytest.fixture
def test_files_bad():
    path = TEST_PATH / "files" / "bad"
    return [p for p in path.glob("*.txt")]
