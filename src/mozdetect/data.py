# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy as np
import pandas
import traceback


class InvalidNumberError(Exception):
    """Raised when an invalid number of points is requested."""

    pass


class UnknownDataTypeError(Exception):
    """Raised when an unknown data type is requested."""

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

    def __init__(self, data, data_type="all", **kwargs):
        """Initializes the time series.

        :param list data: A list of tuples representing the time series.
        :param str/list data_type: The data type that should be iterated over. See
            `set_data_type` for more information.
        :param kwargs: A set of options that can be used to finetune the
            options passed into the pandas DataFrame creation.
        """
        self._original_data = self._prepare_data(data, **kwargs)
        self._iteration_data = self._original_data
        self._data_type = "all"

        self._numerical_data = self.get_numerical_columns()
        self._nonnumerical_data = self.get_nonnumerical_columns()

        # Only set data type after getting the numberical, and
        # non-numerical columns from the original data
        self.set_data_type(data_type)

        self._currind = 0
        self._curr = None

    def __iter__(self):
        """Helper method to iterate over the timeseries.

        :return DataFrame: A row in the DataFrame.
        """
        for index, row in self.data.iterrows():
            self._currind = index
            self._curr = row

            yield self._curr

    @property
    def data(self):
        return self._iteration_data

    def _prepare_data(self, data, **kwargs):
        """Formats the data into a pandas DataFrame for detectors.

        Note that since the DataFrame doesn't have restrictions on types,
        multiple types can be combined into a single tuple, e.g. (1, 2, "h")
        is valid. As is the following when data is missing: [(1, 2), (3, 4, 5)]

        :param list data: A list of tuples representing the time series.
        :param kwargs: A set of options that can be used to finetune the
            options passed into the pandas DataFrame creation.

        :return DataFrame: The data converted to a pandas DataFrame.
        """
        return pandas.DataFrame(data=data, **kwargs)

    def set_data_type(self, data_type):
        """Used to set the data type to iterate over.

        By default, all the data will be iterated over. If "numerical" is passed
        here, then only the numerical data will be returned in all methods. If
        "non-numerical" is passed, then only the non-numerical data will be returned.
        This can be reset to all data by passing "all". A custom type may also
        be passed for special returns.

        :param str/list data_type: Either "numerical", "non-numerical", or "all" to
            denote the type of data. Alternatively, pass a list of custom types to get
            alternative data.
        """
        self._data_type = data_type
        if isinstance(self._data_type, str):
            if self._data_type == "numerical":
                self._iteration_data = self._numerical_data
            elif self._data_type == "non-numerical":
                self._iteration_data = self._nonnumerical_data
            elif self._data_type == "all":
                self._iteration_data = self._original_data
            else:
                raise UnknownDataTypeError(
                    f"Unknown data type requested for iteration: {self._data_type}"
                )
        elif isinstance(self._data_type, list):
            try:
                self._iteration_data = self._original_data.select_dtypes(include=self._data_type)
            except Exception:
                raise UnknownDataTypeError(
                    f"Failed to get custom data types for {str(self._data_type)}:"
                    f" {traceback.format_exc()}"
                )
        else:
            raise UnknownDataTypeError("Expecting list or str as type for data type.")

    def get_current(self):
        """Returns the current datum being analyzed.

        :return DataFrame: The row at the current position in the DataFrame.
        """
        if self._curr is None:
            self._curr = self.data.iloc[[self._currind]]
        return self._curr

    def get_next_n(self, n):
        """Returns the next `n` data points in the time series.

        This methods is exclusive, and doesn't include the current data point
        that is being analyzed.

        :param int n: The number of data points to get.

        :return DataFrame: The number of requested rows if they exist. If the
            current position is at the end of the timeseries, then nothing will
            be returned.
        """
        if n <= 0:
            raise InvalidNumberError("Number of data points must be greater than 0.")
        return self.data.iloc[self._currind + 1 : self._currind + n + 1]

    def get_previous_n(self, n):
        """Returns the previous `n` data points in the time series.

        This methods is exclusive, and doesn't include the current data point
        that is being analyzed.

        :param int n: The number of data points to get.

        :return DataFrame: The number of requested rows if they exist. If the
            current position is at the beginning of the timeseries, then nothing will
            be returned.
        """
        if n <= 0:
            raise InvalidNumberError("Number of data points must be greater than 0.")
        return self.data.iloc[max(self._currind - n, 0) : self._currind]

    def get_numerical_columns(self):
        """Returns the data but with only numerical columns.

        :return DataFrame: Returns the data with non-numerical columns removed.
        """
        return self.data.select_dtypes(include=[np.number])

    def get_nonnumerical_columns(self):
        """Returns the data but with only non-numerical columns.

        :return DataFrame: Returns the data with numerical columns removed.
        """
        return self.data.select_dtypes(exclude=[np.number])
