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

## Testing Change Detection Techniques

This section provides an overview about how to add and test new or existing change detection techniques.

### Adding New Techniques

All techniques are defined in two parts. The first part is the detector itself that compares two (or more) groups to each other, and returns the result of that comparison. The second part is a timeseries detector that runs across a full timeseries (e.g. a TelemetryTimeSeries) and uses the detector from the first part to detect changes.

Both of these should be defined for any new techniques. This makes it possible to make different timeseries detectors using the same underlying detector technique. See `src/mozdetect/detectors/cdf_squared.py` for an example implementation of a detector, and `src/mozdetect/detectors/cdf_squared.py` for an example implementation of the timeseries detector. Note that the detectors will need to be subclasses of the `BaseDetector`, and `BaseTimeSeriesDetector`, respectively.

The `TelemetryTimeSeries` object provides an interface for accessing the data with some helper methods. However, if those are not enough, it's possible to access the raw data that the time series object was built with through `TelemetryTimeSeries.raw_data`.

The detector only needs to return a dictionary with information about the comparison. However, the timeseries detector must return a list of `Detection` objects that contain information about the changes detected.

### Testing Techniques

After the new technique was added, create a new testing script. This script can exist anywhere, but there's a special folder that can be added to the top-level of the repo called `sample-scripts` that can contain the script and it will be ignored when making commits. See the example in `examples/sample_detection_run.py` for how to run the detection. It can be run using the following from the top-level of the repo:
```
uv run examples/sample_detection_run.py
```

At the moment, the only detection techniques available use data from BigQuery. This means that you will need to login locally, and ensure that you have access to the `mozdata` project. Follow [these instructions](https://cloud.google.com/sdk/docs/install) for how to install the tool, then run the following to login and set the project:
```
gcloud auth login --update-adc
gcloud config set project mozdata
```

The key things to do in the script are calling `get_metric_table` to get the data, creating a `TelemetryTimeSeries` with the data, and then calling the change detection technique with the timeseries object as an argument. The change detection technique class is obtained from `mozdetect.get_timeseries_detectors()["name-of-detector"]`. Calling `detect_changes()` on the resulting object will trigger the change detection, and return a list of `Detection` objects that describe the change that was detected.

### Using New Techniques in Alerting/Monitoring

Once a new technique is added, a new release of mozdetect will need to be produced. From there, an update in Treeherder will be needed for the mozdetect package along with a new deployment. Once deployed, it will be usable.

Currently, mozdetect is only used for alerting on telemetry probes so in the `monitor` field that is added to the probe(s), the field `change_detection_technique` will need to be used to specify the name of the change detection technique that was added. Additional arguments to the technique can also be provided through the `change_detection_args` field.


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
