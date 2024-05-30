from typing import Optional, Union

import chardet
from chardet.universaldetector import UniversalDetector

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


def is_ascii(s: Union[bytes, bytearray]) -> bool:
    """Return `True` if *string* is ASCII."""
    return chardet.detect(s)["encoding"] in ALLOWED_ENCODINGS


def get_non_ascii_words(filename: str) -> set[str]:
    """Return a set of all non-ASCII words from *filename*."""
    words = set()
    with open(filename, "rb") as fh:
        for line in fh.readlines():
            for word in line.strip().split():
                if not is_ascii(word):
                    words.add(word.decode())
    return words
