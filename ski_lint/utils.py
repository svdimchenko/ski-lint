from typing import Optional

import chardet
from chardet.universaldetector import UniversalDetector

from .line_analysis_result import LineAnalysisResult

ALLOWED_ENCODINGS = (None, "ascii")


def get_encoding(*filenames: str) -> dict[str, chardet.ResultDict]:
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
        with open(filename, "rb") as fh:
            for line in fh.readlines():
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        encodings[filename] = detector.result
    return encodings


def get_non_ascii_files(*filenames: str) -> dict[str, Optional[str]]:
    """Return dict of `filename: encoding` for files with not allowed encoding."""
    encoding_info = get_encoding(*filenames)
    return {
        filename: info["encoding"]
        for filename, info in encoding_info.items()
        if info["encoding"] not in ALLOWED_ENCODINGS
    }


def get_non_ascii_lines(filename: str) -> list[LineAnalysisResult]:
    """Return all lines with non-ASCII chars from *filename*."""

    results = []
    with open(filename) as f:
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

    context = line[start_index:end_index]

    return context
