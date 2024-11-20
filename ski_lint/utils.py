"""SKI LINT utilities."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from chardet.universaldetector import UniversalDetector

if TYPE_CHECKING:
    import chardet

ALLOWED_ENCODINGS = (None, "ascii")


class LineAnalysisResult:
    """The line analysis result object."""

    def __init__(self, line_num: int, line: str) -> None:
        self.line_num = line_num
        self.line = line.rstrip("\r\n")
        self.chars: dict[str, list[int]] = {}

    def add_char(self, char: str, char_pos: int) -> None:
        """Add character to the char list."""
        self.chars.setdefault(char, []).append(char_pos)


def get_encoding(filenames: list[str]) -> dict[str, chardet.ResultDict]:
    """Return encoding information for *filenames*.

    E.g.:

    {
        '__init__.py': {'encoding': 'ascii', 'confidence': 1.0, 'language': ''},
        '__main__.py': {'encoding': 'ascii', 'confidence': 1.0, 'language': ''},
        'cli.py': {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}
        'utils.py': {'encoding': 'ascii', 'confidence': 1.0, 'language': ''}
    }

    """
    detector = UniversalDetector()
    encodings = {}
    for filename in filenames:
        detector.reset()
        with Path(filename).open("rb") as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encodings[filename] = detector.result
    return encodings


def get_non_ascii_files(filenames: list[str]) -> dict[str, str | None]:
    """Return dict of `filename: encoding` for files with not allowed encoding."""
    encoding_info = get_encoding(filenames)
    return {
        filename: info["encoding"]
        for filename, info in encoding_info.items()
        if info["encoding"] not in ALLOWED_ENCODINGS
    }


def get_non_ascii_lines(filename: str) -> list[LineAnalysisResult]:
    """Return all lines with non-ASCII chars from *filename*."""
    results = []
    with Path(filename).open() as f:
        for line_num, line in enumerate(f, start=1):
            result = LineAnalysisResult(line_num, line)

            for char_pos, char in enumerate(line, start=1):
                if not char.isascii():
                    result.add_char(char, char_pos)

            if result.chars:
                results.append(result)

    return results


def extract_context(line: str, center_position: int, context_width: int) -> str:
    """Return a context of the lines containing non-ASCII characters."""
    chars_before = context_width // 2
    chars_after = context_width // 2

    start_index = max(0, center_position - chars_before)
    end_index = min(len(line), center_position + chars_after)

    return line[start_index:end_index]
