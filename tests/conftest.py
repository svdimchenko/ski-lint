import pathlib

import pytest

TEST_PATH = pathlib.Path(__file__).parent.resolve()
BASE_PATH = TEST_PATH.parent
EXPECTED_VERSION = "0.2.3"


@pytest.fixture
def exp_version():
    return EXPECTED_VERSION


@pytest.fixture
def test_files_good():
    path = TEST_PATH / "files" / "good"
    return [p for p in path.glob("*.txt")]


@pytest.fixture
def test_files_bad():
    path = TEST_PATH / "files" / "bad"
    return [p for p in path.glob("*.txt")]
