# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from unittest import mock

from mozdetect.telemetry_query import get_metric_table


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_fog(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Windows", use_fog=True)

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "os = 'Windows'" in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_fog_all_platforms(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "All", use_fog=True)

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "AND os" not in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_non_fog(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Windows", process="content")

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "os = 'Windows'" in query
    assert "glam_desktop_nightly_aggregates" in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient", new=mock.MagicMock())
def test_telemetry_query_non_fog_missing_process():
    with pytest.raises(ValueError):
        get_metric_table("fake_probe", "Windows")


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_android(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Android", android=True)

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "os = 'Android'" in query
    assert "glam_fenix_nightly_aggregates" in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_android_missing_flag(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Android")

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "os = 'Android'" in query
    assert "glam_fenix_nightly_aggregates" in query
