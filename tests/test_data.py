# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from mozdetect.data import InvalidNumberError, TimeSeries


def test_data():
    ts = TimeSeries([(1, 2, 3), (4, 5, 6)])

    # Check that the first row is returned
    assert (ts.get_current() == (1, 2, 3)).all(axis=1).any()

    # Check second time to make sure it doesn't change
    assert (ts.get_current() == (1, 2, 3)).all(axis=1).any()


def test_data_empty():
    ts = TimeSeries([])
    assert len(ts.data) == 0

    with pytest.raises(IndexError):
        ts.get_current()


def test_data_iteration():
    data = [(1, 2, 3), (4, 5, 6)]
    ts = TimeSeries(data)

    for row in ts:
        assert (row == data[ts._currind]).all().any()


def test_data_complex():
    ts = TimeSeries([(1, 2, "h"), (4, 5, "e", 5)])
    assert (ts.get_current() == (1, 2, "h", None)).all().any()
    assert ts.get_current().isna().loc[0, 3]


def test_data_get_n():
    ts = TimeSeries([(1, 2, 3), (4, 5, 6), (3, 5, 5)])

    subset = ts.get_next_n(2)
    assert all((subset == row).all(axis=1).any() for row in [(4, 5, 6), (3, 5, 5)])
    assert not (subset == (1, 2, 3)).all(axis=1).any()

    # Returns empty as there is nothing before the first element
    subset = ts.get_previous_n(1)
    assert subset.empty

    ts._currind += 2
    subset = ts.get_previous_n(2)
    assert all((subset == row).all(axis=1).any() for row in [(1, 2, 3), (4, 5, 6)])
    assert not (subset == (3, 5, 5)).all(axis=1).any()

    # Returns empty as there is nothing after the last element
    subset = ts.get_next_n(1)
    assert subset.empty


def test_data_get_bad_n():
    ts = TimeSeries([])
    with pytest.raises(InvalidNumberError):
        ts.get_next_n(-1)

    with pytest.raises(InvalidNumberError):
        ts.get_previous_n(-1)
