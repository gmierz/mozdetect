# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from mozdetect.detectors.base import BaseDetector
from mozdetect.detectors.cdf import CDFDetector
from mozdetect.detectors.cdf_squared import CDFSquaredDetector

DETECTORS = {"base": BaseDetector, "cdf": CDFDetector, "cdf_squared": CDFSquaredDetector}


def get_detectors():
    return DETECTORS
