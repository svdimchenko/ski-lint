"""A pre-commit hook, that rejects files containing non-ASCII characters."""

import logging
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from importlib.metadata import version

from omegaconf import OmegaConf, ValidationError

from .utils import extract_context, get_non_ascii_files, get_non_ascii_lines

logging.basicConfig(
    format="{asctime} - {levelname} - {message}",
    level=logging.INFO,
    style="{",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

description = __doc__.strip()


@dataclass
class DefaultConfig:
    accepted_values: list[str] = field(default_factory=list)
    check: bool = False
    config_file: str = ".ski-lint.yml"
    context_width: int = 50
    filenames: list[str] = field(default_factory=list)


def get_args() -> Namespace:
    ap = ArgumentParser(description=description)
    ap.add_argument("--version", action="version", version=version("ski_lint"))
    ap.add_argument(
        "--check",
        action="store_true",
        help="return code is `1`, when non-ASCII files are found",
    )
    ap.add_argument("filenames", nargs="+", metavar="FILENAME", help="path to the files to check")
    ap.add_argument("--context-width", type=int, help="width of the context of the non-ASCII line")
    ap.add_argument("--config-file", type=str, help="path to config file")
    args = ap.parse_args()
    return args


def run(config: OmegaConf) -> int:
    bad_encodings = get_non_ascii_files(config.filenames)
    accepted_chars = [chr(int(value[2:], 16)) for value in config.accepted_values]

    has_non_ascii_files = False

    if bad_encodings:
        for filename, encoding in bad_encodings.items():
            non_ascii_lines = get_non_ascii_lines(filename)

            for line_result in non_ascii_lines:
                for char, char_positions in line_result.chars.items():
                    if char not in accepted_chars:
                        has_non_ascii_files = True
                        for char_pos in char_positions:
                            context = extract_context(line_result.line, char_pos, config.context_width)
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

    if config.check and has_non_ascii_files:
        return 1

    if not has_non_ascii_files:
        log.info("NON-ASCII CHECK: OK")

    return 0


def main() -> None:
    args = get_args()

    try:
        # Defaults and type validation
        config = OmegaConf.structured(DefaultConfig)

        # Config file (optional)
        config_file = args.config_file or config.config_file
        try:
            config = OmegaConf.merge(
                config,
                OmegaConf.load(config_file),
            )
        except FileNotFoundError:
            pass

        # CLI args filtered dict (highest priority)
        filtered_args_dict = {k: v for k, v in vars(args).items() if v is not None}
        config = OmegaConf.merge(
            config,
            OmegaConf.create(filtered_args_dict),
        )

        OmegaConf.set_readonly(config, True)

        sys.exit(run(config))
    except ValidationError as e:
        log.error(f"Configuration error: {e}")
        sys.exit(1)
