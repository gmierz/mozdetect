# mozdetect
A python package containing change point detection techniques for use at Mozilla.

# Setup, and Development

## Pre-commit checks

Pre-commit linting checks must be setup like this (run within the top-level of this repo directory):

```
python -m pip install pre-commit
pre-commit install
```

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

Next, run the following to build the package, and install dependencies:

```
uv sync
```

Run a script that uses the built module with the following:

```
uv run my_script.py
```
