# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pandas


class BaseTimeSeriesDetector:
    """Base timeseries detector that detectors must inherit from."""

    def __init__(self, timeseries, **kwargs):
        """Initialize the BaseTimeSeriesDetector.

        :param TimeSeries timeseries: A TimeSeries object that represents
            the timeseries to analyze.
        """
        self.timeseries = timeseries
        if hasattr(self.timeseries, "set_data_type"):
            self.timeseries.set_data_type("numerical")

    def get_sum_of_previous_n(self, n, inclusive=False):
        """Returns the sum of the past n data points.

        :param int n: The number of data points to sum.
        :param bool inclusive: If true, include the current point in the sum.
        :return DataFrame: A single data point as the sum of the previous n data points.
        """
        previous_n = self.timeseries.get_previous_n(n, inclusive=inclusive)
        if previous_n.empty:
            return previous_n
        return pandas.DataFrame(previous_n.sum()).T

    def get_sum_of_next_n(self, n, inclusive=True):
        """Returns the sum of the past n data points.

        :param int n: The number of data points to sum.
        :param bool inclusive: If true, include the current point in the sum.
        :return DataFrame: A single data point as the sum of the next n data points.
        """
        next_n = self.timeseries.get_next_n(n, inclusive=inclusive)
        if next_n.empty:
            return next_n
        return pandas.DataFrame(next_n.sum()).T

    def get_avg_of_previous_n(self, n, inclusive=False):
        """Returns the average of the past n data points.

        :param int n: The number of data points to average.
        :param bool inclusive: If true, include the current point in the average.
        :return DataFrame: A single data point as the average of the previous n data points.
        """
        previous_n = self.timeseries.get_previous_n(n, inclusive=inclusive)
        if previous_n.empty:
            return previous_n
        return pandas.DataFrame(previous_n.mean()).T

    def get_avg_of_next_n(self, n, inclusive=True):
        """Returns the average of the next n data points.

        :param int n: The number of data points to sum.
        :param bool inclusive: If true, include the current point in the average.
        :return DataFrame: A single data point as the average of the next n data points.
        """
        next_n = self.timeseries.get_next_n(n, inclusive=inclusive)
        if next_n.empty:
            return next_n
        return pandas.DataFrame(next_n.mean()).T

    def get_avg_of_surrounding_n(self, n):
        pn = int(n / 2)
        if n % 2 == 1:
            nn = pn + 1
        else:
            nn = pn

        currind = self.timeseries._currind
        data = self.timeseries.data.iloc[currind - pn : currind + nn + 1]
        return pandas.DataFrame(data.mean()).T

    def get_avg_of_next_surrounding_n(self, n):
        pn = int(n / 2)
        if n % 2 == 1:
            nn = pn + 1
        else:
            nn = pn

        currind = self.timeseries._currind
        data = self.timeseries.data.iloc[currind - pn + 1 : currind + nn + 2]
        return pandas.DataFrame(data.mean()).T

    def detect_changes(self, **kwargs):
        """Detect changes in a timeseries.

        :return: A list of Detection objects representing the regressions found.
        """
        pass
