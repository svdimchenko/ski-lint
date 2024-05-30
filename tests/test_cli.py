import logging
import subprocess
from importlib.metadata import version

from ski_lint import run


def test_cli_version(exp_version):
    cmd = ["ski-lint", "--version"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert res.stdout.strip() == version("ski_lint")


def test_files_output_good(caplog, test_files_good):
    with caplog.at_level(logging.INFO):
        exp = "- NON-ASCII CHECK: OK"
        run(*test_files_good)
        assert exp in caplog.text


def test_files_output_bad(caplog, test_files_bad):
    exp = [
        "tests/files/bad/special.txt (Windows-1252): 'there…'",
        "tests/files/bad/umlaut.txt (utf-8): 'föur', 'käle', 'Åir'",
    ]
    run(*test_files_bad)
    assert all([e in caplog.text for e in exp])


def test_check_mode_good(test_files_good):
    cmd = ["ski-lint", "--check", *test_files_good]
    res = subprocess.run(cmd)
    assert res.returncode == 0


def test_check_mode_bad(test_files_bad):
    cmd = ["ski-lint", "--check", *test_files_bad]
    res = subprocess.run(cmd)
    assert res.returncode == 1
