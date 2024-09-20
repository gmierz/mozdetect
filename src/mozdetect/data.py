# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pandas


class InvalidNumberError(Exception):
    """Raised when an invalid number of points is requested."""

    pass


class TimeSeries:
    """Represents a time series composed of Datum objects.

    Primarily a wrapper around `pandas.DataFrame`. It provides some additional
    helper functions to make it simpler to iterate over the data, and provide
    a common interface for all detectors to use.

    The pandas.DataFrame was chosen for this so that strings could be included
    in the dataset alongside numerical input. It also easily allows multidimensional
    data to be used.
    """

    def __init__(self, data, **kwargs):
        """Initializes the time series.

        :param list data: A list of tuples representing the time series.
        :param kwargs: A set of options that can be used to finetune the
            options passed into the pandas DataFrame creation.
        """
        self.data = self._prepare_data(data, **kwargs)
        self._currind = 0
        self._curr = None

    def __iter__(self):
        for index, row in self.data.iterrows():
            self._currind = index
            self._curr = row

            yield self._curr

    def _prepare_data(self, data, **kwargs):
        """Formats the data into a pandas DataFrame for detectors.

        Note that since the DataFrame doesn't have restrictions on types,
        multiple types can be combined into a single tuple, e.g. (1, 2, "h")
        is valid. As is the following when data is missing: [(1, 2), (3, 4, 5)]

        :param list data: A list of tuples representing the time series.
        :param kwargs: A set of options that can be used to finetune the
            options passed into the pandas DataFrame creation.
        """
        return pandas.DataFrame(data=data, **kwargs)

    def get_current(self):
        """Returns the current datum being analyzed."""
        if self._curr is None:
            self._curr = self.data.iloc[[self._currind]]
        return self._curr

    def get_next_n(self, n):
        """Returns the next `n` data points in the time series.

        This methods is exclusive, and doesn't include the current data point
        that is being analyzed.

        :param int n: The number of data points to get.
        """
        if n <= 0:
            raise InvalidNumberError("Number of data points must be greater than 0.")
        return self.data.iloc[self._currind + 1 : self._currind + n + 1]

    def get_previous_n(self, n):
        """Returns the previous `n` data points in the time series.

        This methods is exclusive, and doesn't include the current data point
        that is being analyzed.

        :param int n: The number of data points to get.
        """
        if n <= 0:
            raise InvalidNumberError("Number of data points must be greater than 0.")
        return self.data.iloc[max(self._currind - n, 0) : self._currind]
