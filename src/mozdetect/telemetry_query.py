# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from google.cloud import bigquery


class BigQueryClient:
    client = None

    def __init__(self, project="moz-fx-data-bq-performance"):
        if BigQueryClient.client is None:
            BigQueryClient.initialize_bq_client()

    @classmethod
    def initialize_bq_client(cls, project="moz-fx-data-bq-performance"):
        BigQueryClient.client = bigquery.Client()


def get_years_to_query():
    current_year = datetime.now().year
    next_year = current_year + 1
    previous_year = current_year - 1
    return previous_year, current_year, next_year


def _get_android_metric_table(probe):
    previous_year, current_year, next_year = get_years_to_query()

    job = BigQueryClient.client.query(
        f"""
        SELECT *
        FROM
            moz-fx-data-shared-prod.glam_etl.glam_fenix_nightly_aggregates
        WHERE
            metric = '{probe}'
            AND ping_type = 'metrics'
            AND os = 'Android'
            AND build_id != '*'
            AND (
                build_id like '{previous_year}%'
                OR build_id like '{current_year}%'
                OR build_id like '{next_year}%'
            )
    """
    )
    return job.to_dataframe()


def _get_non_fog_desktop_metric_table(probe, process, os):
    previous_year, current_year, next_year = get_years_to_query()

    job = BigQueryClient.client.query(
        f"""
        SELECT *
        FROM
            moz-fx-data-shared-prod.glam_etl.glam_desktop_nightly_aggregates
        WHERE
            metric ='{probe}'
            AND process = "{process}"
            AND os = '{os}'
            AND build_id != "*"
            AND (
                build_id like '{previous_year}%'
                OR build_id like '{current_year}%'
                OR build_id like '{next_year}%'
            )
        ORDER BY build_id
    """
    )

    return job.to_dataframe()


def _get_fog_desktop_metric_table(probe, os):
    previous_year, current_year, next_year = get_years_to_query()

    job = BigQueryClient.client.query(
        f"""
        SELECT *
        FROM
            moz-fx-data-shared-prod.glam_etl.glam_fog_nightly_aggregates
        WHERE
            metric ='{probe}'
            AND ping_type = "*"
            AND os = '{os}'
            AND build_id != "*"
            AND (
                build_id like '{previous_year}%'
                OR build_id like '{current_year}%'
                OR build_id like '{next_year}%'
            )
        ORDER BY build_id
    """
    )
    return job.to_dataframe()


def get_metric_table(probe, os, process=None, android=False, use_fog=False):
    BigQueryClient()

    print("Running query...")
    if android:
        return _get_android_metric_table(probe, os, process)
    elif not use_fog:
        if process is None:
            raise ValueError("Missing process argument for non-fog telemetry probes.")
        return _get_non_fog_desktop_metric_table(probe, process, os)
    else:
        return _get_fog_desktop_metric_table(probe, os)
