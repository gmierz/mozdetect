# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pandas

from pandas.testing import assert_frame_equal

from mozdetect import get_detectors, get_timeseries_detectors
from mozdetect.detectors import BaseDetector
from mozdetect.timeseries_detectors import BaseTimeSeriesDetector, Detection

from tests.support import get_sample_telemetry_data


class TestDetector(BaseDetector, detector_name="test"):
    __test__ = False

    def detect_changes(self):
        return {"detection": True}


class TestTimeSeriesDetector(BaseTimeSeriesDetector, timeseries_detector_name="test"):
    __test__ = False

    def detect_changes(self):
        detector = TestDetector()

        detections = []
        for i in range(5):
            detection = detector.detect_changes()
            detections.append(
                Detection(
                    previous_value=i,
                    new_value=i + 1,
                    confidence=detection["detection"],
                    location="somewhere",
                    direction="up",
                )
            )

        return detections


def get_ts_detector():
    sample_data = get_sample_telemetry_data()
    return TestTimeSeriesDetector(sample_data)


def test_get_detectors():
    detectors = get_detectors()
    assert len(detectors) >= 1
    assert "test" in detectors


def test_get_timeseries_detectors():
    ts_detectors = get_timeseries_detectors()
    assert len(ts_detectors) >= 1
    assert "test" in ts_detectors


def test_detector_basic():
    ts_detector = get_ts_detector()
    detections = ts_detector.detect_changes()
    assert len(detections) == 5
    assert detections[0].previous_value == 0 and detections[0].confidence


def test_detector_get_data():
    ts_detector = get_ts_detector()

    ts_detector.timeseries._currind = 2
    res = ts_detector.get_sum_of_previous_n(2, inclusive=True)
    assert_frame_equal(res, pandas.DataFrame([[0, 2, 4, 6, 8, 10]]))

    ts_detector.timeseries._currind = 0
    res = ts_detector.get_sum_of_next_n(3)
    assert_frame_equal(res, pandas.DataFrame([[0, 3, 6, 9, 12, 15]]))
