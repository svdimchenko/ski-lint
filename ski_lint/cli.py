"""A pre-commit hook, that rejects files containing non-ASCII characters."""

import logging
import sys
from argparse import ArgumentParser, Namespace
from importlib.metadata import version

from .utils import get_non_ascii_files, get_non_ascii_words

logging.basicConfig(format="{asctime} - {levelname} - {message}", level=logging.INFO, style="{", stream=sys.stdout)
log = logging.getLogger(__name__)

description = __doc__.strip()


def get_args() -> Namespace:
    ap = ArgumentParser(description=description)
    ap.add_argument("--version", action="version", version=version("ski_lint"))
    ap.add_argument(
        "--check",
        action="store_true",
        help="return code is `1`, when non-ASCII files are found",
    )
    ap.add_argument("filenames", nargs="+", metavar="FILENAME", help="path to the files to check")
    args = ap.parse_args()
    return args


def run(*filenames: str, check: bool = False) -> int:
    bad_encodings = get_non_ascii_files(*filenames)
    if bad_encodings:
        for filename, encoding in bad_encodings.items():
            words = get_non_ascii_words(filename)
            words_str = ", ".join([f"'{w}'" for w in sorted(words)])
            log.error(f"- {filename} ({encoding}): {words_str}")
    else:
        log.info("- NON-ASCII CHECK: OK")

    if bad_encodings and check:
        return 1
    else:
        return 0


def main() -> None:
    args = get_args()
    sys.exit(run(*args.filenames, check=args.check))
