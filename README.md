# Enforce ASCII

<!-- markdownlint-disable MD013 -->

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

<!-- markdownlint-restore -->

A Python package to find files containing non-ASCII encoded characters.
If you find any bugs, issues or anything, please use the [issue tracker](https://github.com/svdimchenko/ski-lint/issues)
on GitHub - issues and PRs are welcome ❤️

## Install

It's on [PyPi] as `ski-lint`, you can install it with _pip_, _pipx_, etc.

```shell
pip install ski-lint
```

## Usage

```shell
$ ski-lint --help
usage: ski-lint [-h] [--version] [--check] [-w CONTEXT_WIDTH] [-c CONFIG_FILE] FILENAME [FILENAME ...]

A pre-commit hook, that rejects files containing non-ASCII characters.

positional arguments:
  FILENAME              path to the files to check

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --check               return code is `1`, when non-ASCII files are found
  -w, --context-width CONTEXT_WIDTH
                        width of the context of the non-ASCII line
  -c, --config-file CONFIG_FILE
                        path to config file
```

`CONFIG_FILE` is an optional yaml file (default `.ski-lint.yml`) in which you can override any CLI argument or add
additional configuration:

```yml
accepted_values:
    - U+E4
    - U+2026
context_width: 50
```

### Example

```shell
$ ski-lint tests/files/*/*.txt
2024-10-03 16:24:50,339 - ERROR - tests/files/bad/special.txt (Windows-1252), line 1, pos 9, char U+2026 '…', context: 'Hi there…'
2024-10-03 16:24:50,339 - ERROR - tests/files/bad/umlaut.txt (utf-8), line 1, pos 349, char U+E4 'ä', context: 'y next level pitchfork käle chips leggings gastrop'
2024-10-03 16:24:50,339 - ERROR - tests/files/bad/umlaut.txt (utf-8), line 1, pos 547, char U+F6 'ö', context: 'gs. Waistcoat jianbing föur dollar toast jean shor'
2024-10-03 16:24:50,339 - ERROR - tests/files/bad/umlaut.txt (utf-8), line 3, pos 190, char U+C5 'Å', context: 'eitan viral photo booth Åir plant cliche neutra la'
2024-10-03 16:24:50,339 - ERROR - tests/files/bad/zero-width-space.txt (Windows-1252), line 1, pos 62, non-printable char U+200B, context: 'ace (U+200B) at the end!U+200B'
```

## Pre-Commit

This can be used as a [pre-commit](https://pre-commit.com/) hook:

```yaml
- repo: https://github.com/svdimchenko/ski-lint
  rev: v0.1.0
  hooks:
      - id: ski-lint
```
