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

Next, run the following to build the package:

```
uv tool install .
```

Run a script that uses the built module with the following:

```
uv run my_script.py
```

## Pre-commit checks

Pre-commit linting checks must be setup like this (run within the top-level of this repo directory). If the tool was already built, then it doesn't need to be built again:

```
uv tool install .
pre-commit install
```