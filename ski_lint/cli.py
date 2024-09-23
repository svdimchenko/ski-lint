"""A pre-commit hook, that rejects files containing non-ASCII characters."""

import logging
import sys
from argparse import ArgumentParser, Namespace
from importlib.metadata import version

from .utils import extract_context, get_non_ascii_files, get_non_ascii_lines

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    level=logging.INFO,
    style="{",
    stream=sys.stdout,
)
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
    ap.add_argument("--context-width", type=int, default=50, help="width of the context of the non-ASCII line")
    args = ap.parse_args()
    return args


def run(*filenames: str, check: bool = False, context_width: int) -> int:
    bad_encodings = get_non_ascii_files(*filenames)

    if bad_encodings:
        for filename, encoding in bad_encodings.items():
            non_ascii_lines = get_non_ascii_lines(filename)

            for line_result in non_ascii_lines:
                for char, char_positions in line_result.chars.items():
                    for char_pos in char_positions:
                        context = extract_context(line_result.line, char_pos, context_width)
                        unicode_notation = f"U+{ord(char):0X}"

                        error_msg = f"{filename} ({encoding}), "
                        error_msg += f"line {line_result.line_num}, "
                        error_msg += f"pos {char_pos}, "
                        if not char.isprintable():
                            error_msg += f"non-printable char {unicode_notation}, "
                            context = context.replace(char, unicode_notation)
                        else:
                            error_msg += f"char {unicode_notation} '{char}', "
                        error_msg += f"context: '{context}'"

                        log.error(error_msg)

    else:
        log.info("NON-ASCII CHECK: OK")

    if bad_encodings and check:
        return 1

    return 0


def main() -> None:
    args = get_args()
    sys.exit(run(*args.filenames, check=args.check, context_width=args.context_width))
