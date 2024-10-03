import logging
import subprocess
from importlib.metadata import version

from omegaconf import OmegaConf
from ski_lint import DefaultConfig, run


def test_cli_version(exp_version):
    cmd = ["ski-lint", "--version"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 0
    assert res.stdout.strip() == version("ski_lint")


def test_files_output_good(caplog, test_files_good):
    with caplog.at_level(logging.INFO):
        exp = "NON-ASCII CHECK: OK"

        config = OmegaConf.merge(
            OmegaConf.structured(DefaultConfig),
            OmegaConf.create({"filenames": test_files_good}),
        )
        run(config)

        assert exp in caplog.text


def test_files_output_bad(caplog, test_files_bad):
    exp = [
        "tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char U+2026 '…', context: 'Hi there…'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char U+E4 'ä', context: 'y next level pitchfork käle chips leggings gastrop'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'gs. Waistcoat jianbing föur dollar toast jean shor'",
        "tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'eitan viral photo booth Åir plant cliche neutra la'",
        "tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'ace (U+200B) at the end!U+200B'",
    ]

    config = OmegaConf.merge(
        OmegaConf.structured(DefaultConfig),
        OmegaConf.create({"filenames": test_files_bad}),
    )
    run(config)
    assert all([e in caplog.text for e in exp])


def test_files_output_bad_accepted_values(caplog, test_files_bad):
    config = OmegaConf.merge(
        OmegaConf.structured(DefaultConfig),
        OmegaConf.create({"filenames": test_files_bad, "accepted_values": ["U+E4", "U+2026"]}),
    )
    run(config)

    exp = [
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'gs. Waistcoat jianbing föur dollar toast jean shor'",
        "tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'eitan viral photo booth Åir plant cliche neutra la'",
        "tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'ace (U+200B) at the end!U+200B'",
    ]
    assert all([e in caplog.text for e in exp])

    not_exp = [
        "tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char '…', context: 'Hi there…'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char 'ä', context: 'y next level pitchfork käle chips leggings gastrop'",
    ]
    assert all([ne not in caplog.text for ne in not_exp])


def test_check_mode_good(test_files_good):
    cmd = ["ski-lint", "--check", *test_files_good]
    res = subprocess.run(cmd)
    assert res.returncode == 0


def test_check_mode_bad(test_files_bad):
    cmd = ["ski-lint", "--check", *test_files_bad]
    res = subprocess.run(cmd)
    assert res.returncode == 1
