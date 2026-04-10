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

    get_metric_table("fake_probe", "Windows", process="content", use_fog=False)

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "os = 'Windows'" in query
    assert "glam_desktop_nightly_aggregates" in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient", new=mock.MagicMock())
def test_telemetry_query_non_fog_missing_process():
    with pytest.raises(ValueError):
        get_metric_table("fake_probe", "Windows", use_fog=False)


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


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_fog_from_build_date(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Windows", use_fog=True, from_build_date="2025-01-01 00:00:00")

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "2025-01-01 00:00:00" in query
    assert "PARSE_DATETIME" in query
    assert "build_id like" not in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_fog_no_from_build_date_uses_year_filter(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Windows", use_fog=True)

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "build_id like" in query
    assert "PARSE_DATETIME" not in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient")
def test_telemetry_query_android_from_build_date(mocked_bq_client):
    mocked_client = mock.MagicMock()
    mocked_bq_client.client = mocked_client

    get_metric_table("fake_probe", "Android", from_build_date="2025-06-15 00:00:00")

    assert len(mocked_client.query.call_args_list) == 1

    query = mocked_client.query.call_args_list[0][0][0]
    assert "fake_probe" in query
    assert "glam_fenix_nightly_aggregates" in query
    assert "2025-06-15 00:00:00" in query
    assert "PARSE_DATETIME" in query
    assert "build_id like" not in query


@mock.patch("mozdetect.telemetry_query.BigQueryClient", new=mock.MagicMock())
def test_telemetry_query_non_fog_from_build_date_raises():
    with pytest.raises(ValueError):
        get_metric_table(
            "fake_probe",
            "Windows",
            process="content",
            use_fog=False,
            from_build_date="2025-01-01 00:00:00",
        )
