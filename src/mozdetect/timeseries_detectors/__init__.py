# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from mozdetect.timeseries_detectors.base import BaseTimeSeriesDetector
from mozdetect.timeseries_detectors.cdf import CDFTimeSeriesDetector
from mozdetect.timeseries_detectors.cdf_squared import CDFSquaredTimeSeriesDetector

TIMESERIES_DETECTORS = {
    "base": BaseTimeSeriesDetector,
    "cdf": CDFTimeSeriesDetector,
    "cdf_squared": CDFSquaredTimeSeriesDetector,
}


def get_timeseries_detectors():
    return TIMESERIES_DETECTORS
