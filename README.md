# mozdetect
A python package containing change point detection techniques for use at Mozilla.

# Setup, and Development

## Setup

Install `uv` first using the following:

```
python -m pip install uv
```

Install `poetry` using the following:

```
python -m pip install poetry
```

## Running

Next, run the following to build the package, and install dependencies. This step can be skipped though since `uv run` will implicitly build the package:

```
uv sync
```

Run a script that uses the built module with the following:

```
uv run my_script.py
```

## Pre-commit checks

Pre-commit linting checks must be setup like this (run within the top-level of this repo directory):

```
uv sync
uv run pre-commit install
```

## Running tests

Tests all reside in the `tests/` folder and can be run using:

```
uv run pytest
```
