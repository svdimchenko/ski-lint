import logging
import subprocess
import tempfile
from importlib.metadata import version

from omegaconf import OmegaConf


def test_cli_version():
    cmd = ["ski-lint", "--version"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 0
    assert res.stdout.strip() == version("ski_lint")


def test_no_files_given():
    exp = "Configuration error: No filenames provided"

    cmd = ["ski-lint"]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert exp in res.stdout
    assert res.returncode == 1


def test_files_output_good(caplog, test_files_good):
    exp = "NON-ASCII CHECK: OK"

    with caplog.at_level(logging.INFO):
        cmd = ["ski-lint", *test_files_good]
        res = subprocess.run(cmd, capture_output=True, text=True)

        assert exp in res.stdout

        with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
            tmp_config.write(
                OmegaConf.to_yaml(
                    OmegaConf.create(
                        {"filenames": [str(f) for f in test_files_good]},
                    )
                )
            )
            tmp_config.flush()

            cmd = ["ski-lint", "--config", tmp_config.name, *test_files_good]
            res = subprocess.run(cmd, capture_output=True, text=True)

            assert exp in res.stdout


def test_files_output_bad(test_files_bad):
    exp = [
        "tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char U+2026 '…', context: 'Hi there…'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char U+E4 'ä', context: 'y next level pitchfork käle chips leggings gastrop'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'gs. Waistcoat jianbing föur dollar toast jean shor'",
        "tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'eitan viral photo booth Åir plant cliche neutra la'",
        "tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'ace (U+200B) at the end!U+200B'",
    ]

    cmd = ["ski-lint", *test_files_bad]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert all([e in res.stdout for e in exp])

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"filenames": [str(f) for f in test_files_bad]},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name]
        res = subprocess.run(cmd, capture_output=True, text=True)

        assert all([e in res.stdout for e in exp])


def test_precedence_cli_options(test_files_bad):
    # Here we use the `--check` option to check if the precedence of the CLI options is correct.
    # The expected precedence is: CLI > config file > default values.

    # Default values

    cmd = ["ski-lint", *test_files_bad]
    res = subprocess.run(cmd)

    assert res.returncode == 0

    # Config file > default values

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"check": True},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, *test_files_bad]
        res = subprocess.run(cmd)

        assert res.returncode == 1

    # CLI > config file > default values

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"check": False},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, "--check", *test_files_bad]
        res = subprocess.run(cmd)

        assert res.returncode == 1


def test_files_output_context_width(test_files_bad):
    exp = [
        "tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char U+2026 '…', context: 'here…'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char U+E4 'ä', context: 'rk käle ch'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'ng föur do'",
        "tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'oth Åir pl'",
        "tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'end!U+200B'",
    ]

    cmd = ["ski-lint", "--context-width", "10", *test_files_bad]
    res = subprocess.run(cmd, capture_output=True, text=True)

    print(res.stdout)

    assert all([e in res.stdout for e in exp])

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"context_width": 10},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, *test_files_bad]
        res = subprocess.run(cmd, capture_output=True, text=True)

        print(res.stdout)

        assert all([e in res.stdout for e in exp])


def test_files_output_bad_accepted_values(test_files_bad):
    exp = [
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'gs. Waistcoat jianbing föur dollar toast jean shor'",
        "tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'eitan viral photo booth Åir plant cliche neutra la'",
        "tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'ace (U+200B) at the end!U+200B'",
    ]

    not_exp = [
        "tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char '…', context: 'Hi there…'",
        "tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char 'ä', context: 'y next level pitchfork käle chips leggings gastrop'",
    ]

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"accepted_values": ["U+E4", "U+2026"]},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, *test_files_bad]
        res = subprocess.run(cmd, capture_output=True, text=True)

        assert all([e in res.stdout for e in exp])
        assert all([ne not in res.stdout for ne in not_exp])


def test_check_mode_good(test_files_good):
    cmd = ["ski-lint", "--check", *test_files_good]
    res = subprocess.run(cmd)

    assert res.returncode == 0

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"check": True},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, *test_files_good]
        res = subprocess.run(cmd)

        assert res.returncode == 0


def test_check_mode_bad(test_files_bad):
    cmd = ["ski-lint", "--check", *test_files_bad]
    res = subprocess.run(cmd)

    assert res.returncode == 1

    with tempfile.NamedTemporaryFile(mode="w") as tmp_config:
        tmp_config.write(
            OmegaConf.to_yaml(
                OmegaConf.create(
                    {"check": True},
                )
            )
        )
        tmp_config.flush()

        cmd = ["ski-lint", "--config", tmp_config.name, *test_files_bad]
        res = subprocess.run(cmd)

        assert res.returncode == 1
