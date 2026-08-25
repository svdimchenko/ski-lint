import pathlib
import sys

import pytest

TEST_PATH = pathlib.Path(__file__).parent.resolve()
BASE_PATH = TEST_PATH.parent
EXPECTED_VERSION = "0.2.3"

# Resolve the ski-lint binary from the same Python environment that's running pytest,
# so subprocess calls work regardless of whether the venv is activated.
SKI_LINT_BIN = str(pathlib.Path(sys.executable).parent / "ski-lint")


@pytest.fixture
def ski_lint_bin():
    return SKI_LINT_BIN


@pytest.fixture
def exp_version():
    return EXPECTED_VERSION


@pytest.fixture
def test_files_good():
    path = TEST_PATH / "files" / "good"
    return list(path.glob("*.txt"))


@pytest.fixture
def test_files_bad():
    path = TEST_PATH / "files" / "bad"
    return list(path.glob("*.txt"))
