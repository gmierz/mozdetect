# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pandas

from mozdetect.data import TelemetryTimeSeries

SAMPLE_DATA = [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]


def get_sample_telemetry_data():
    """Use this method to get a TelemetryTimeSeries object populated with some sample data."""
    df = pandas.DataFrame(SAMPLE_DATA)
    return TelemetryTimeSeries(df)
