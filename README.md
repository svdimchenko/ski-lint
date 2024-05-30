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
usage: ski-lint [-h] [--version] [--check] FILENAME [FILENAME ...]

A pre-commit hook, that rejects files containing non ASCII characters.

positional arguments:
  FILENAME    path to the files to check

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --check     return code is `1`, when non-ASCII files are found
```

### Example

```shell
$ ski-lint tests/files/*/*.txt
- tests/files/bad/special.txt (Windows-1252): 'there…'
- tests/files/bad/umlaut.txt (utf-8): 'föur', 'käle', 'Åir'
```

## Pre-Commit

This can be used as a [pre-commit](https://pre-commit.com/) hook:

```yaml
- repo: https://github.com/svdimchenko/ski-lint
  rev: v0.1.0
  hooks:
      - id: ski-lint
```
