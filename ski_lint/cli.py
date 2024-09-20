"""A pre-commit hook, that rejects files containing non-ASCII characters."""

import logging
import sys
from argparse import ArgumentParser, Namespace
from importlib.metadata import version
from pathlib import Path
from typing import Any

import yaml

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
    ap.add_argument("--config", type=str, default=".ski-lint.yml", help="path to config file")
    args = ap.parse_args()
    return args


def get_config(filename: str) -> dict[str, Any]:
    config = {}
    config_file = Path(filename)
    if config_file.exists():
        with open(config_file) as yaml_file:
            config = yaml.safe_load(yaml_file)
            config = {} if config is None else config
    return config


def run(*filenames: str, check: bool = False, context_width: int, accepted_chars: list[str] = []) -> int:
    bad_encodings = get_non_ascii_files(*filenames)

    has_non_ascii_files = False

    if bad_encodings:
        for filename, encoding in bad_encodings.items():
            non_ascii_lines = get_non_ascii_lines(filename)

            for line_result in non_ascii_lines:
                for char, char_positions in line_result.chars.items():
                    if char not in accepted_chars:
                        has_non_ascii_files = True
                        for char_pos in char_positions:
                            context = extract_context(line_result.line, char_pos, context_width)

                            error_msg = f"{filename} ({encoding}), "
                            error_msg += f"line {line_result.line_num}, "
                            error_msg += f"pos {char_pos}, "
                            if not char.isprintable():
                                error_msg += f"non-printable char U+{ord(char):0x}, "
                                context = context.replace(char, f"U+{ord(char):0x}")
                            else:
                                error_msg += f"char '{char}', "
                            error_msg += f"context: '{context}'"

                            log.error(error_msg)

    if check and has_non_ascii_files:
        return 1

    if not has_non_ascii_files:
        log.info("NON-ASCII CHECK: OK")

    return 0


def main() -> None:
    args = get_args()
    config = get_config(args.config)

    accepted_chars = [chr(int(value[2:], 16)) for value in config.get("accepted_values", [])]

    sys.exit(run(*args.filenames, check=args.check, context_width=args.context_width, accepted_chars=accepted_chars))
