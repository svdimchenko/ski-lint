from pathlib import Path

import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]

SOURCE_DIRECTORY = Path("ski_lint").resolve()
TEST_DIRECTORY = Path("tests").resolve()

TOOLS_TEST = [
    "pytest",
    ".",
]

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run pytest test suit for Python versions."""
    session.install(*TOOLS_TEST)
    args = session.posargs if session.posargs else [str(TEST_DIRECTORY)]
    session.run("pytest", *args)
