# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


class BaseTimeSeriesDetector:
    """Base timeseries detector that detectors must inherit from."""

    def __init__(self, timeseries, **kwargs):
        """Initialize the BaseTimeSeriesDetector.

        :param TimeSeries timeseries: A TimeSeries object that represents
            the timeseries to analyze.
        """
        self.timeseries = timeseries

    def detect_changes(self):
        """Detect changes in a timeseries.

        :return: A list of Detection objects representing the regressions found.
        """
        pass
